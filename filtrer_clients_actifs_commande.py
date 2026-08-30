#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A la selection du client dans une commande, n'affiche plus que les
clients ACTIFS (Clients::statut = true, ou jamais renseigné pour les
clients crees avant l'ajout de ce champ).

Un client BLOQUE (statut = false) deja associe a une commande
existante reste neanmoins visible/selectionne quand on MODIFIE cette
commande precise (sinon le formulaire d'edition casserait sur les
anciennes commandes) -- mais il n'apparait plus dans la liste pour une
NOUVELLE commande ni pour les autres clients.

Usage:
    python3 filtrer_clients_actifs_commande.py /chemin/vers/successImprim
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


ANCIEN_IMPORTS = """use Symfony\\Component\\Form\\FormBuilderInterface;
use Symfony\\Component\\OptionsResolver\\OptionsResolver;
use Symfony\\Component\\Validator\\Constraints\\GreaterThanOrEqual;
use Symfony\\Component\\Validator\\Constraints\\NotNull;
use Symfony\\Component\\Validator\\Constraints\\Valid;
use App\\Entity\\CommandesDetails;
use Symfony\\Component\\Form\\Extension\\Core\\Type\\ChoiceType;
use Doctrine\\ORM\\EntityRepository;

class CommandesType extends AbstractType
{
    public function buildForm(
        FormBuilderInterface $builder,
        array $options
    ): void {
        $builder
            ->add('clients', EntityType::class, [
                'class' => Clients::class,
                'choice_label' => static function (
                    Clients $client
                ): string {
                    $telephone = $client->getTelephone()
                        ?: 'Sans téléphone';

                    $prenom = trim(
                        (string) $client->getPrenom()
                    );

                    $nom = trim(
                        (string) $client->getNom()
                    );

                    return trim(sprintf(
                        '%s — %s %s',
                        $telephone,
                        $prenom,
                        $nom
                    ));
                },
                'placeholder' => 'Sélectionnez un client',
                'required' => true,
                'choice_attr' => static function (
                    Clients $client
                ): array {
                    return [
                        'data-type-client' => $client->getTypeClient(),
                    ];
                },
                'attr' => [
                    'class' => 'form-select js-select-search',
                    'data-placeholder'
                        => 'Téléphone, prénom ou nom...',
                ],
                'constraints' => [
                    new NotNull(
                        message: 'Veuillez sélectionner un client.'
                    ),
                ],
            ])

            ->add('dateLivraison', DateTimeType::class, ["""

NOUVEAU_IMPORTS = """use Symfony\\Component\\Form\\FormBuilderInterface;
use Symfony\\Component\\Form\\FormEvent;
use Symfony\\Component\\Form\\FormEvents;
use Symfony\\Component\\OptionsResolver\\OptionsResolver;
use Symfony\\Component\\Validator\\Constraints\\GreaterThanOrEqual;
use Symfony\\Component\\Validator\\Constraints\\NotNull;
use Symfony\\Component\\Validator\\Constraints\\Valid;
use App\\Entity\\CommandesDetails;
use Symfony\\Component\\Form\\Extension\\Core\\Type\\ChoiceType;
use Doctrine\\ORM\\EntityRepository;

class CommandesType extends AbstractType
{
    /**
     * N'affiche que les clients actifs (statut = true, ou jamais
     * renseigné pour les anciens clients créés avant ce champ).
     *
     * $inclureClientId permet de garder visible, en modification, le
     * client déjà associé à la commande même s'il a été bloqué depuis
     * — sinon le formulaire d'édition casserait sur les anciennes
     * commandes.
     */
    private function optionsChampClients(?int $inclureClientId = null): array
    {
        return [
            'class' => Clients::class,
            'query_builder' => static function (
                EntityRepository $er
            ) use ($inclureClientId) {
                $qb = $er->createQueryBuilder('c')
                    ->orderBy('c.nom', 'ASC');

                if ($inclureClientId !== null) {
                    $qb
                        ->andWhere('c.statut = :actif OR c.statut IS NULL OR c.id = :clientActuel')
                        ->setParameter('clientActuel', $inclureClientId);
                } else {
                    $qb->andWhere('c.statut = :actif OR c.statut IS NULL');
                }

                return $qb->setParameter('actif', true);
            },
            'choice_label' => static function (
                Clients $client
            ): string {
                $telephone = $client->getTelephone()
                    ?: 'Sans téléphone';

                $prenom = trim(
                    (string) $client->getPrenom()
                );

                $nom = trim(
                    (string) $client->getNom()
                );

                return trim(sprintf(
                    '%s — %s %s',
                    $telephone,
                    $prenom,
                    $nom
                ));
            },
            'placeholder' => 'Sélectionnez un client',
            'required' => true,
            'choice_attr' => static function (
                Clients $client
            ): array {
                return [
                    'data-type-client' => $client->getTypeClient(),
                ];
            },
            'attr' => [
                'class' => 'form-select js-select-search',
                'data-placeholder'
                    => 'Téléphone, prénom ou nom...',
            ],
            'constraints' => [
                new NotNull(
                    message: 'Veuillez sélectionner un client.'
                ),
            ],
        ];
    }

    public function buildForm(
        FormBuilderInterface $builder,
        array $options
    ): void {
        $builder
            ->add(
                'clients',
                EntityType::class,
                $this->optionsChampClients()
            )

            ->addEventListener(
                FormEvents::PRE_SET_DATA,
                function (FormEvent $event): void {
                    $commande = $event->getData();

                    $clientActuel = $commande instanceof Commandes
                        ? $commande->getClients()
                        : null;

                    if (
                        $clientActuel === null
                        || $clientActuel->isStatut() !== false
                    ) {
                        return;
                    }

                    $event->getForm()->add(
                        'clients',
                        EntityType::class,
                        $this->optionsChampClients(
                            $clientActuel->getId()
                        )
                    );
                }
            )

            ->add('dateLivraison', DateTimeType::class, ["""

MARQUEUR = "optionsChampClients"


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

    if ANCIEN_IMPORTS not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc introuvable -> abandon (rien ecrit).")
        print("  Votre fichier reel differe probablement du brouillon a cet endroit.")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B3 -A45 \"add('clients', EntityType\" " + chemin_relatif)
        return False

    contenu_corrige = contenu.replace(ANCIEN_IMPORTS, NOUVEAU_IMPORTS, 1)

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

    chemin_relatif = "src/Form/CommandesType.php"

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
        print("Le champ Client (nouvelle commande / modification) n'affiche")
        print("plus que les clients actifs. Un client bloqué déjà associé à")
        print("une commande existante reste visible sur CETTE commande-là,")
        print("pour ne pas casser l'édition des anciennes commandes.")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
