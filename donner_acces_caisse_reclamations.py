#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Donne explicitement au role ROLE_CAISSE_COMMANDE le droit de payer les
reclamations, sans dependre de la hierarchie des roles (qui peut ne
pas etre a jour cote serveur) : chaque verification d'acces accepte
desormais ROLE_TRESORERIE_SAISIR OU ROLE_CAISSE_COMMANDE, explicitement.

Corrige aussi un probleme lie : la liste des reclamations ne montrait
"toutes les reclamations" (avec la colonne Agent) qu'aux administrateurs
-- une caisse habilitee a payer ne voyait que SES PROPRES reclamations
et n'aurait donc jamais pu tomber sur celles des autres agents a payer.

Modifie 2 fichiers :
  1) src/Controller/ReclamationController.php
  2) templates/reclamation/index.html.twig

Usage:
    python3 donner_acces_caisse_reclamations.py /chemin/vers/successImprim
"""

import os
import sys
import shutil
import subprocess


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


PHP_LINT_DISPONIBLE = shutil.which("php") is not None


def lint_php_si_possible(chemin_absolu):
    if not PHP_LINT_DISPONIBLE:
        return
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=10,
        )
        sortie = (resultat.stdout + resultat.stderr).strip()
        if resultat.returncode == 0:
            print("  php -l : OK")
        else:
            print("  [ATTENTION] php -l a signale un probleme :")
            print("  " + sortie.replace("\n", "\n  "))
    except Exception as exc:
        print("  (php -l ignore : " + repr(exc) + ")")


def appliquer_blocs_verifie(racine, chemin_relatif, marqueur, blocs):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu_original = f.read()

    if marqueur in contenu_original:
        print("[SKIP] " + chemin_relatif + " contient deja '" + marqueur + "' (deja applique).")
        return True

    contenu = contenu_original
    for idx, (ancien, nouveau) in enumerate(blocs, start=1):
        occurrences = contenu.count(ancien)
        if occurrences != 1:
            print("[ECHEC] " + chemin_relatif + " : bloc " + str(idx) + "/" + str(len(blocs)) +
                  " trouve " + str(occurrences) + " fois au lieu de 1 -> abandon (rien ecrit sur ce fichier).")
            print("  Extrait attendu (debut) : " + repr(ancien[:150]))
            return False
        contenu = contenu.replace(ancien, nouveau, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (" + str(len(blocs)) + " bloc(s) applique(s))")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    if chemin_relatif.endswith(".php"):
        lint_php_si_possible(chemin_absolu)
    return True


# ============================================================
# 1) src/Controller/ReclamationController.php
# ============================================================

CTRL_BLOC_1_ANCIEN = """        $user = $this->utilisateurConnecte();
        $estAdmin = $this->isGranted('ROLE_ADMIN');
        $peutPayer = $this->isGranted('ROLE_TRESORERIE_SAISIR');

        $reclamations = $estAdmin
            ? $reclamationRepository->findToutes()
            : $reclamationRepository->findPourAgent($user);

        return $this->render('reclamation/index.html.twig', [
            'reclamations' => $reclamations,
            'estAdmin' => $estAdmin,
            'peutPayer' => $peutPayer,
        ]);
    }"""

CTRL_BLOC_1_NOUVEAU = """        $user = $this->utilisateurConnecte();
        $estAdmin = $this->isGranted('ROLE_ADMIN');
        $peutPayer = $this->isGranted('ROLE_TRESORERIE_SAISIR')
            || $this->isGranted('ROLE_CAISSE_COMMANDE');

        /*
         * Un agent ne voit que ses propres réclamations. Un admin ou
         * une caisse habilitée à payer doit voir toutes les
         * réclamations de tout le monde, sinon il ne peut jamais
         * tomber sur celles des autres agents à payer.
         */
        $reclamations = ($estAdmin || $peutPayer)
            ? $reclamationRepository->findToutes()
            : $reclamationRepository->findPourAgent($user);

        return $this->render('reclamation/index.html.twig', [
            'reclamations' => $reclamations,
            'estAdmin' => $estAdmin,
            'peutPayer' => $peutPayer,
        ]);
    }"""

CTRL_BLOC_2_ANCIEN = """        return $this->render('reclamation/show.html.twig', [
            'reclamation' => $reclamation,
            'peutValider' => $this->isGranted('ROLE_ADMIN'),
            'peutPayer' => $this->isGranted('ROLE_TRESORERIE_SAISIR'),
            'peutVoirTresorerie' => $this->isGranted('ROLE_TRESORERIE_VOIR'),
        ]);
    }"""

CTRL_BLOC_2_NOUVEAU = """        return $this->render('reclamation/show.html.twig', [
            'reclamation' => $reclamation,
            'peutValider' => $this->isGranted('ROLE_ADMIN'),
            'peutPayer' => $this->isGranted('ROLE_TRESORERIE_SAISIR')
                || $this->isGranted('ROLE_CAISSE_COMMANDE'),
            'peutVoirTresorerie' => $this->isGranted('ROLE_TRESORERIE_VOIR'),
        ]);
    }"""

CTRL_BLOC_3_ANCIEN = """    #[Route('/{id}/payer', name: 'payer', requirements: ['id' => '\\d+'], methods: ['GET', 'POST'])]
    #[IsGranted('ROLE_TRESORERIE_SAISIR')]
    public function payer(
        Reclamation $reclamation,
        Request $request,
        EntityManagerInterface $entityManager,
        MouvementTresorerieService $mouvementTresorerieService
    ): Response {
        if (!$reclamation->isValidee()) {"""

CTRL_BLOC_3_NOUVEAU = """    #[Route('/{id}/payer', name: 'payer', requirements: ['id' => '\\d+'], methods: ['GET', 'POST'])]
    public function payer(
        Reclamation $reclamation,
        Request $request,
        EntityManagerInterface $entityManager,
        MouvementTresorerieService $mouvementTresorerieService
    ): Response {
        if (
            !$this->isGranted('ROLE_TRESORERIE_SAISIR')
            && !$this->isGranted('ROLE_CAISSE_COMMANDE')
        ) {
            throw $this->createAccessDeniedException(
                'Vous n’avez pas le droit de payer une réclamation.'
            );
        }

        if (!$reclamation->isValidee()) {"""

CTRL_BLOC_4_ANCIEN = """    private function verifierAccesReclamation(Reclamation $reclamation): void
    {
        if ($this->isGranted('ROLE_ADMIN') || $this->isGranted('ROLE_TRESORERIE_SAISIR')) {
            return;
        }"""

CTRL_BLOC_4_NOUVEAU = """    private function verifierAccesReclamation(Reclamation $reclamation): void
    {
        if (
            $this->isGranted('ROLE_ADMIN')
            || $this->isGranted('ROLE_TRESORERIE_SAISIR')
            || $this->isGranted('ROLE_CAISSE_COMMANDE')
        ) {
            return;
        }"""

CTRL_MARQUEUR = "ROLE_CAISSE_COMMANDE');"


# ============================================================
# 2) templates/reclamation/index.html.twig
# ============================================================

TWIG_BLOC_1_ANCIEN = """				{{ estAdmin ? 'Toutes les réclamations' : 'Mes réclamations' }}"""
TWIG_BLOC_1_NOUVEAU = """				{{ (estAdmin or peutPayer) ? 'Toutes les réclamations' : 'Mes réclamations' }}"""

TWIG_BLOC_2_ANCIEN = """							<th>Référence</th>
							{% if estAdmin %}
								<th>Agent</th>
							{% endif %}"""
TWIG_BLOC_2_NOUVEAU = """							<th>Référence</th>
							{% if estAdmin or peutPayer %}
								<th>Agent</th>
							{% endif %}"""

TWIG_BLOC_3_ANCIEN = """								{% if estAdmin %}
									<td>
										{{ reclamation.agent.employe.prenom|default('') }}
										{{ reclamation.agent.employe.nom|default(reclamation.agent.username) }}
									</td>
								{% endif %}"""
TWIG_BLOC_3_NOUVEAU = """								{% if estAdmin or peutPayer %}
									<td>
										{{ reclamation.agent.employe.prenom|default('') }}
										{{ reclamation.agent.employe.nom|default(reclamation.agent.username) }}
									</td>
								{% endif %}"""

TWIG_BLOC_4_ANCIEN = """								<td colspan="{{ estAdmin ? 8 : 7 }}" class="text-center text-muted">"""
TWIG_BLOC_4_NOUVEAU = """								<td colspan="{{ (estAdmin or peutPayer) ? 8 : 7 }}" class="text-center text-muted">"""

TWIG_MARQUEUR = "estAdmin or peutPayer"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    if not PHP_LINT_DISPONIBLE:
        print("(info : commande 'php' introuvable ici, le controle 'php -l' sera saute)")
        print()

    resultats = []

    print("-" * 70)
    print("1) src/Controller/ReclamationController.php")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "src/Controller/ReclamationController.php",
        CTRL_MARQUEUR,
        [
            (CTRL_BLOC_1_ANCIEN, CTRL_BLOC_1_NOUVEAU),
            (CTRL_BLOC_2_ANCIEN, CTRL_BLOC_2_NOUVEAU),
            (CTRL_BLOC_3_ANCIEN, CTRL_BLOC_3_NOUVEAU),
            (CTRL_BLOC_4_ANCIEN, CTRL_BLOC_4_NOUVEAU),
        ]
    ))
    print()

    print("-" * 70)
    print("2) templates/reclamation/index.html.twig")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "templates/reclamation/index.html.twig",
        TWIG_MARQUEUR,
        [
            (TWIG_BLOC_1_ANCIEN, TWIG_BLOC_1_NOUVEAU),
            (TWIG_BLOC_2_ANCIEN, TWIG_BLOC_2_NOUVEAU),
            (TWIG_BLOC_3_ANCIEN, TWIG_BLOC_3_NOUVEAU),
            (TWIG_BLOC_4_ANCIEN, TWIG_BLOC_4_NOUVEAU),
        ]
    ))
    print()

    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Connectez-vous avec un compte ROLE_CAISSE_COMMANDE :")
        print("- la liste des reclamations doit maintenant montrer TOUTES les")
        print("  reclamations de tous les agents (colonne Agent visible) ;")
        print("- le bouton 'Payer' doit apparaitre sur une reclamation validee ;")
        print("- le paiement doit fonctionner (compte limite a sa propre caisse")
        print("  et aux comptes partages, comme livre precedemment).")
    else:
        print("Au moins un fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
