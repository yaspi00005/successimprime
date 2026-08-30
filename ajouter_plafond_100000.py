#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1) Supprime la "regle des 3 mois" en pre-presse (RÈGLE 1 du controle
   de credit client) : un client recent sans avance n'est plus
   automatiquement bloque. Seule reste la RÈGLE 2 (encours anterieur
   > plafond de credit).

2) Change le plafond de credit par defaut a 100 000 pour les
   NOUVEAUX clients (src/Entity/Clients.php).

3) Ajoute une commande console pour donner ce meme plafond de
   100 000 aux clients DEJA enregistres qui n'en ont pas encore
   (plafond a 0 ou vide). Elle ne touche jamais un client qui a deja
   un plafond configure manuellement, et fonctionne en mode "apercu"
   par defaut :

     php bin/console app:clients:initialiser-plafond-credit
     php bin/console app:clients:initialiser-plafond-credit --confirmer

Ensuite, vous pourrez reduire manuellement le plafond de tel ou tel
client au cas par cas, comme d'habitude (fiche client).

Usage:
    python3 ajouter_plafond_100000.py /chemin/vers/successImprim
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


def php_lint(chemin_absolu):
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=30
        )
        print("  php -l : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass


# ============================================================
# 1) Suppression de la regle des 3 mois
# ============================================================

ANCIEN_BLOC_REGLE_3_MOIS = """        /*
         * ============================================================
         * RÈGLE 1
         *
         * CLIENT DE MOINS DE 3 MOIS
         * ============================================================
         *
         * Nouveau client / client récent
         * +
         * aucune avance validée
         *
         * => INTERDICTION PRODUCTION
         * ============================================================
         */

        if (
            $clientMoinsDeTroisMois
            &&
            $avanceCommandeActuelle <= 0
        ) {
            return $this->resultat(
                autorise: false,

                motif:
                    'Production bloquée : ce client a moins de 3 mois d’ancienneté et aucune avance validée n’a été enregistrée sur la commande actuelle.',

                ancienneteMois:
                    $ancienneteMois,

                clientRecent:
                    true,

                plafondCredit:
                    $plafondCredit,

                totalCommande:
                    $totalCommandeActuelle,

                avanceCommande:
                    $avanceCommandeActuelle,

                resteCommande:
                    $resteCommandeActuelle
            );
        }


"""

MOTIF_DEJA_SUPPRIME = "Production bloquée : ce client a moins de 3 mois"


def corriger_controle_credit(racine):
    chemin_relatif = "src/Service/ControleCreditClientService.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MOTIF_DEJA_SUPPRIME not in contenu:
        print("[SKIP] " + chemin_relatif + " : la règle des 3 mois est déjà absente (déjà appliqué).")
        return True

    if ANCIEN_BLOC_REGLE_3_MOIS not in contenu:
        print("[ECHEC] " + chemin_relatif + " : le bloc à supprimer ne correspond pas exactement -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B3 -A35 \"RÈGLE 1\" " + chemin_relatif)
        return False

    contenu_corrige = contenu.replace(ANCIEN_BLOC_REGLE_3_MOIS, "", 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_corrige)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_corrige:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (règle des 3 mois supprimée)")
    php_lint(chemin_absolu)
    return True


# ============================================================
# 2) Plafond par defaut = 100000 pour les nouveaux clients
# ============================================================

def corriger_entite_clients(racine):
    chemin_relatif = "src/Entity/Clients.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print()
    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    ancien = "private ?int $plafondCredit = 0;"
    nouveau = "private ?int $plafondCredit = 100000;"

    if nouveau in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + nouveau + "' (deja applique).")
        return True

    if ancien not in contenu:
        print("[ECHEC] " + chemin_relatif + " : ligne '" + ancien + "' introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n \"plafondCredit = \" " + chemin_relatif)
        return False

    contenu_corrige = contenu.replace(ancien, nouveau, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_corrige)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_corrige:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (plafond par defaut = 100000)")
    php_lint(chemin_absolu)
    return True


# ============================================================
# 3) Nouvelle commande console (fichier neuf)
# ============================================================

CONTENU_COMMANDE = '''<?php

namespace App\\Command;

use App\\Repository\\ClientsRepository;
use Doctrine\\ORM\\EntityManagerInterface;
use Symfony\\Component\\Console\\Attribute\\AsCommand;
use Symfony\\Component\\Console\\Command\\Command;
use Symfony\\Component\\Console\\Input\\InputInterface;
use Symfony\\Component\\Console\\Input\\InputOption;
use Symfony\\Component\\Console\\Output\\OutputInterface;

#[AsCommand(
    name: 'app:clients:initialiser-plafond-credit',
    description: 'Donne un plafond de crédit par défaut aux clients qui n’en ont pas encore un.'
)]
final class InitialiserPlafondCreditClientsCommand extends Command
{
    private const PLAFOND_PAR_DEFAUT = 100000;

    public function __construct(
        private readonly ClientsRepository $clientsRepository,
        private readonly EntityManagerInterface $entityManager
    ) {
        parent::__construct();
    }

    protected function configure(): void
    {
        $this->addOption(
            'confirmer',
            null,
            InputOption::VALUE_NONE,
            'Applique réellement le changement (sans cette option, la commande ne fait qu’un aperçu, sans rien modifier).'
        );
    }

    protected function execute(
        InputInterface $input,
        OutputInterface $output
    ): int {
        /*
         * Ne touche jamais un client qui a déjà un plafond configuré
         * (0 ou une valeur négative comptent comme "jamais configuré").
         */
        $clients = $this->clientsRepository->findAll();

        $concernes = [];

        foreach ($clients as $client) {
            if ((int) $client->getPlafondCredit() <= 0) {
                $concernes[] = $client;
            }
        }

        if ($concernes === []) {
            $output->writeln(
                '<info>Tous les clients ont déjà un plafond de crédit configuré. Rien à faire.</info>'
            );

            return Command::SUCCESS;
        }

        $output->writeln(sprintf(
            '<comment>%d client(s) sans plafond de crédit (0 ou vide) recevront un plafond de %s FCFA :</comment>',
            count($concernes),
            number_format(self::PLAFOND_PAR_DEFAUT, 0, ',', ' ')
        ));

        foreach ($concernes as $client) {
            $output->writeln(sprintf(
                '  - #%d %s (plafond actuel : %d)',
                $client->getId(),
                $client->getNomComplet(),
                (int) $client->getPlafondCredit()
            ));
        }

        if (!$input->getOption('confirmer')) {
            $output->writeln('');
            $output->writeln(
                '<comment>Aperçu uniquement, rien n’a été modifié. Relancez avec --confirmer pour appliquer.</comment>'
            );

            return Command::SUCCESS;
        }

        foreach ($concernes as $client) {
            $client->setPlafondCredit(self::PLAFOND_PAR_DEFAUT);
        }

        $this->entityManager->flush();

        $output->writeln('');
        $output->writeln(sprintf(
            '<info>%d client(s) mis à jour avec un plafond de %s FCFA.</info>',
            count($concernes),
            number_format(self::PLAFOND_PAR_DEFAUT, 0, ',', ' ')
        ));

        return Command::SUCCESS;
    }
}
'''


def creer_commande(racine):
    chemin_relatif = "src/Command/InitialiserPlafondCreditClientsCommand.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print()
    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    if os.path.isfile(chemin_absolu):
        print("[SKIP] " + chemin_relatif + " existe deja (deja applique).")
        return True

    dossier = os.path.dirname(chemin_absolu)
    os.makedirs(dossier, exist_ok=True)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(CONTENU_COMMANDE)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != CONTENU_COMMANDE:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (nouveau fichier cree)")
    php_lint(chemin_absolu)
    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    resultats = [
        corriger_controle_credit(racine),
        corriger_entite_clients(racine),
        creer_commande(racine),
    ]

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("1) La règle des 3 mois ne bloque plus la production en pré-presse.")
        print("   Seul le dépassement du plafond de crédit bloque encore.")
        print()
        print("2) Un nouveau client créé aura desormais 100 000 FCFA de plafond")
        print("   par défaut (modifiable sur sa fiche).")
        print()
        print("3) Pour donner ce même plafond aux clients DEJA enregistrés qui")
        print("   n'en ont pas encore (plafond à 0), lancez d'abord un aperçu :")
        print("     php bin/console app:clients:initialiser-plafond-credit")
        print("   puis, si la liste vous convient, appliquez réellement :")
        print("     php bin/console app:clients:initialiser-plafond-credit --confirmer")
        print()
        print("   Un client qui a déjà un plafond configuré (même à une valeur")
        print("   basse) n'est jamais touché par cette commande — vous gardez")
        print("   la main pour réduire le plafond de tel ou tel client au cas")
        print("   par cas, comme d'habitude sur sa fiche.")
    else:
        print("Au moins un fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
