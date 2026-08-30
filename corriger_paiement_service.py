#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le crash "Call to undefined method
App\\Entity\\MouvementTresorerie::setCompteTresorerie()" lors de la
validation d'un paiement (chèque ou autre).

Cause : PaiementService::valider() et ::annuler() appelaient des
methodes qui n'existent pas sur MouvementTresorerie
(setCompteTresorerie, setSens, setOrigine, valider(), estValide(),
annuler()) -- probablement un reste d'une version anterieure de
l'entite. La vraie API actuelle utilise setCompteDestination(),
setType()/setCategorie(), et le service MouvementTresorerieService
(enregistrer() / annulerValide()) deja utilise ailleurs dans
l'application (decaissements automatiques notamment).

Ce script :
  - injecte MouvementTresorerieService dans PaiementService ;
  - reconstruit le mouvement de tresorerie avec les bons champs
    (type ENCAISSEMENT, categorie VENTE, compte destination) et
    passe par enregistrer() (qui credite le compte immediatement,
    sauf pour un compte bancaire qui reste en attente de
    rapprochement, comme partout ailleurs dans l'application) ;
  - corrige la meme faille dans annuler() (isValide() au lieu
    d'estValide(), annulerValide() au lieu d'un annuler() qui
    n'existe pas).

Usage:
    python3 corriger_paiement_service.py /chemin/vers/successImprim
"""

import os
import subprocess
import sys


def erreur_fatale(message):
    print("\n[ERREUR FATALE] " + message)
    sys.exit(1)


def verifier_racine(racine):
    print("=" * 70)
    print("DIAGNOSTIC DE L'EMPLACEMENT")
    print("=" * 70)
    print("Repertoire courant (pwd)      : " + os.getcwd())
    print("Racine passee en argument     : " + racine)
    print("Racine resolue (chemin absolu): " + os.path.realpath(racine))

    composer_json = os.path.join(racine, "composer.json")
    if not os.path.isfile(composer_json):
        erreur_fatale(
            "Aucun 'composer.json' trouve dans " + os.path.realpath(racine) + "\n"
            "  => Relancez le script en pointant vers la racine du projet."
        )
    print("[OK] composer.json trouve : c'est bien la racine du projet.")
    print()


ANCIEN_CONSTRUCTEUR = """final class PaiementService
{
    public function __construct(
        private readonly EntityManagerInterface $entityManager
    ) {
    }"""

NOUVEAU_CONSTRUCTEUR = """final class PaiementService
{
    public function __construct(
        private readonly EntityManagerInterface $entityManager,
        private readonly MouvementTresorerieService $mouvementTresorerieService
    ) {
    }"""

ANCIEN_VALIDER = """            $mouvement = new MouvementTresorerie();

            $mouvement
                ->setCompteTresorerie($compte)
                ->setPaiement($paiement)
                ->setSens(MouvementTresorerie::SENS_CREDIT)
                ->setOrigine(MouvementTresorerie::ORIGINE_PAIEMENT)
                ->setMontant($paiement->getMontant())
                ->setReferenceExterne(
                    $this->construireReferencePaiement($paiement)
                )
                ->setLibelle(
                    $this->construireLibellePaiement($paiement)
                )
                ->setObservation($paiement->getObservation());

            /*
             * Cette méthode crédite le compte et mémorise
             * le solde avant et après.
             */
            $mouvement->valider();

            $this->entityManager->persist($mouvement);
            $this->entityManager->flush();"""

NOUVEAU_VALIDER = """            $mouvement = new MouvementTresorerie();

            $mouvement
                ->setType(MouvementTresorerie::TYPE_ENCAISSEMENT)
                ->setCategorie(MouvementTresorerie::CATEGORIE_VENTE)
                ->setCompteDestination($compte)
                ->setMontant($paiement->getMontant())
                ->setReferenceExterne(
                    $this->construireReferencePaiement($paiement)
                )
                ->setLibelle(
                    $this->construireLibellePaiement($paiement)
                )
                ->setObservation($paiement->getObservation());

            $paiement->setMouvementTresorerie($mouvement);

            /*
             * enregistrer() crédite immédiatement le compte, sauf
             * s’il s’agit d’un compte bancaire : le mouvement reste
             * alors en attente d’une validation manuelle distincte
             * (rapprochement bancaire).
             */
            $this->mouvementTresorerieService->enregistrer($mouvement);"""

ANCIEN_ANNULER = """            if (!$mouvement->estValide()) {
                throw new \\LogicException(
                    'Le mouvement de ce paiement n’est pas dans un état annulable.'
                );
            }

            $compte = $paiement->getCompteTresorerie();

            if ($compte === null) {
                throw new \\LogicException(
                    'Aucun compte de trésorerie n’est associé au paiement.'
                );
            }

            $this->entityManager->lock(
                $compte,
                LockMode::PESSIMISTIC_WRITE
            );

            $this->entityManager->refresh($compte);

            /*
             * annuler() exécute l’opération inverse :
             * le crédit initial devient un débit.
             */
            $mouvement->annuler($motif);
            $paiement->annuler($motif, $utilisateur);"""

NOUVEAU_ANNULER = """            if (!$mouvement->isValide()) {
                throw new \\LogicException(
                    'Le mouvement de ce paiement n’est pas dans un état annulable.'
                );
            }

            $compte = $paiement->getCompteTresorerie();

            if ($compte === null) {
                throw new \\LogicException(
                    'Aucun compte de trésorerie n’est associé au paiement.'
                );
            }

            /*
             * annulerValide() verrouille les comptes concernés,
             * contrepasse le crédit initial (devient un débit) et
             * marque le mouvement comme annulé.
             */
            $this->mouvementTresorerieService->annulerValide($mouvement, $motif);
            $paiement->annuler($motif, $utilisateur);"""

MARQUEUR = "mouvementTresorerieService"


def corriger_fichier(racine, chemin_relatif):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + MARQUEUR + "' (deja applique).")
        return True

    if ANCIEN_CONSTRUCTEUR not in contenu:
        print("[ECHEC] " + chemin_relatif + " : constructeur introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -A6 \"final class PaiementService\" " + chemin_relatif)
        return False

    if ANCIEN_VALIDER not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc valider() introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B2 -A25 \"setCompteTresorerie\" " + chemin_relatif)
        return False

    if ANCIEN_ANNULER not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc annuler() introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B5 -A15 \"mouvement->annuler\" " + chemin_relatif)
        return False

    contenu_corrige = contenu.replace(ANCIEN_CONSTRUCTEUR, NOUVEAU_CONSTRUCTEUR, 1)
    contenu_corrige = contenu_corrige.replace(ANCIEN_VALIDER, NOUVEAU_VALIDER, 1)
    contenu_corrige = contenu_corrige.replace(ANCIEN_ANNULER, NOUVEAU_ANNULER, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_corrige)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_corrige:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))

    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=30
        )
        print("  php -l : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass

    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "src/Service/PaiementService.php"

    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    resultat = corriger_fichier(racine, chemin_relatif)
    print()

    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if resultat:
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Valider un paiement (chèque ou autre mode) ne doit plus")
        print("planter. Pour un compte bancaire, le mouvement créé reste")
        print("en attente de validation manuelle (rapprochement bancaire),")
        print("comme pour tous les autres mouvements de ce type.")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
