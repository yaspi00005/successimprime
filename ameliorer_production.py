#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regroupe plusieurs ameliorations du module Production :

  1) Corrige le plantage "Appel a la fonction membre getNom() sur null"
     au demarrage d'une production (machine_id jamais soumis par le
     formulaire -> on retombe desormais sur la machine deja detectee
     par IP).
  2) Ajoute une alerte "Nouvelle impression demarree" (ROLE_ADMIN et
     ROLE_PRODUCTION) au demarrage d'un ordre.
  3) Trie la liste de production par priorite (urgente > haute >
     normale > basse) puis par anciennete, au lieu du seul ordre
     d'arrivee.
  4) Ajoute les colonnes "Designation" et "Qte a imprimer" a la liste
     de production.
  5) Sort la gestion des consommables de la fiche d'un ordre de
     production : nouvel ecran independant "Consommables" accessible
     depuis le menu (Production > Consommables).

Modifie 6 fichiers existants et en cree 2 nouveaux :
  - src/Controller/ProductionController.php
  - src/Repository/OrdreProductionRepository.php
  - src/Service/StockService.php
  - templates/production/index.html.twig
  - templates/production/show.html.twig
  - templates/base.html.twig
  - src/Controller/ConsommablesController.php        (nouveau)
  - templates/consommables/index.html.twig            (nouveau)

Usage:
    python3 ameliorer_production.py /chemin/vers/successImprim
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


def creer_fichier_verifie(racine, chemin_relatif, contenu_attendu):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if os.path.isfile(chemin_absolu):
        with open(chemin_absolu, "r", encoding="utf-8") as f:
            contenu_existant = f.read()
        if contenu_existant == contenu_attendu:
            print("[SKIP] " + chemin_relatif + " existe deja et est identique (deja applique).")
            return True
        print("[ECHEC] " + chemin_relatif + " existe deja mais avec un contenu different -> abandon (rien ecrit).")
        return False

    dossier = os.path.dirname(chemin_absolu)
    if dossier and not os.path.isdir(dossier):
        os.makedirs(dossier, exist_ok=True)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_attendu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_attendu:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (fichier cree, " + str(len(contenu_attendu)) + " octets)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    if chemin_relatif.endswith(".php"):
        lint_php_si_possible(chemin_absolu)
    return True


# ============================================================
# 1) src/Controller/ProductionController.php
# ============================================================

CTRL_BLOC_IMPORTS_ANCIEN = r"""use App\Entity\Articles;
use App\Entity\StockSorties;
use App\Repository\ArticlesRepository;"""

CTRL_BLOC_IMPORTS_NOUVEAU = r"""use App\Entity\StockSorties;"""

CTRL_BLOC_SHOW_ANCIEN = r"""    public function show(
        OrdreProduction $ordre,
        Request $request,
        ArticlesRepository $articlesRepository,
        EntityManagerInterface $em
    ): Response {
        /** @var Machines|null $machineCourante */
        $machineCourante = $request->attributes->get(
            '_production_machine'
        );

        $detail = $ordre->getCommandeDetail();

        $consommables = $detail === null
            ? []
            : $em->getRepository(StockSorties::class)->findBy(
                [
                    'commandeDetail' => $detail,
                    'origine' => StockSorties::ORIGINE_MANUELLE,
                    'referenceOrigine' => $ordre->getNumero(),
                ],
                ['date' => 'DESC']
            );

        return $this->render(
            'production/show.html.twig',
            [
                'ordre' => $ordre,
                'machineCourante' => $machineCourante,
                'adresseIpCourante' => $request->getClientIp(),
                'articlesConsommables' => $articlesRepository->findConsommables(),
                'consommables' => $consommables,
            ]
        );
    }"""

CTRL_BLOC_SHOW_NOUVEAU = r"""    public function show(
        OrdreProduction $ordre,
        Request $request
    ): Response {
        /** @var Machines|null $machineCourante */
        $machineCourante = $request->attributes->get(
            '_production_machine'
        );

        return $this->render(
            'production/show.html.twig',
            [
                'ordre' => $ordre,
                'machineCourante' => $machineCourante,
                'adresseIpCourante' => $request->getClientIp(),
            ]
        );
    }"""

CTRL_BLOC_DEMARRER_SIGNATURE_ANCIEN = r"""    public function demarrer(
        OrdreProduction $ordre,
        Request $request,
        MachinesRepository $machinesRepository,
        EntityManagerInterface $em
    ): Response {"""

CTRL_BLOC_DEMARRER_SIGNATURE_NOUVEAU = r"""    public function demarrer(
        OrdreProduction $ordre,
        Request $request,
        MachinesRepository $machinesRepository,
        EntityManagerInterface $em,
        NotificationService $notificationService
    ): Response {"""

CTRL_BLOC_DEMARRER_CORPS_ANCIEN = r"""            $ordre->demarrer(
                $utilisateur,
                $machine
            );

            /*
         * Une seule sauvegarde pour les deux objets.
         */
            $em->flush();

            $this->addFlash(
                'success',
                sprintf(
                    'La production a démarré sur la machine %s.',
                    $machine->getNom()
                )
            );"""

CTRL_BLOC_DEMARRER_CORPS_NOUVEAU = r"""            $ordre->demarrer(
                $utilisateur,
                $machine
            );

            /*
         * NOTIFICATION
         *
         * Prévient les admins/responsables production qu'une
         * nouvelle impression vient de démarrer.
         */
            $notificationService->notifierRoles(
                ['ROLE_ADMIN', 'ROLE_PRODUCTION'],
                sprintf(
                    'Nouvelle impression démarrée : ordre %s%s.',
                    $ordre->getNumero(),
                    $machine !== null ? ' sur ' . $machine->getNom() : ''
                ),
                'app_production_show',
                ['id' => $ordre->getId()],
                $utilisateur
            );

            /*
         * Une seule sauvegarde pour les deux objets.
         */
            $em->flush();

            $this->addFlash(
                'success',
                sprintf(
                    'La production a démarré sur la machine %s.',
                    $machine?->getNom() ?? 'du poste'
                )
            );"""

CTRL_BLOC_RECUPERER_MACHINE_ANCIEN = r"""    private function recupererMachine(
        Request $request,
        MachinesRepository $machinesRepository
    ): mixed {
        $machineId = $request->request->getInt('machine_id');

        if ($machineId < 1) {
            return null;
        }

        $machine = $machinesRepository->find($machineId);

        if ($machine === null) {
            throw new \InvalidArgumentException(
                'La machine sélectionnée est introuvable.'
            );
        }

        return $machine;
    }"""

CTRL_BLOC_RECUPERER_MACHINE_NOUVEAU = r"""    private function recupererMachine(
        Request $request,
        MachinesRepository $machinesRepository
    ): ?Machines {
        $machineId = $request->request->getInt('machine_id');

        if ($machineId < 1) {
            /*
             * Aucun machine_id soumis : on retombe sur la machine
             * détectée par ProductionMachineSubscriber via l'adresse
             * IP du poste (déjà garantie non nulle pour toute route
             * app_production_*, sinon la requête aurait été refusée
             * avant d'arriver ici).
             */
            $machineDetectee = $request->attributes->get('_production_machine');

            return $machineDetectee instanceof Machines ? $machineDetectee : null;
        }

        $machine = $machinesRepository->find($machineId);

        if ($machine === null) {
            throw new \InvalidArgumentException(
                'La machine sélectionnée est introuvable.'
            );
        }

        return $machine;
    }"""

CTRL_BLOC_SUPPRESSION_CONSOMMABLE_ANCIEN = r"""    /**
     * Enregistre un consommable utilisé pendant la production
     * (non prévu dans la nomenclature du produit) : retiré
     * immédiatement du stock disponible.
     */
    #[Route(
        '/{id}/consommable/ajouter',
        name: 'ajouter_consommable',
        requirements: ['id' => '\d+'],
        methods: ['POST']
    )]
    public function ajouterConsommable(
        OrdreProduction $ordre,
        Request $request,
        ArticlesRepository $articlesRepository,
        StockService $stockService
    ): Response {
        $this->verifierJeton(
            $request,
            'production_ajouter_consommable_' . $ordre->getId()
        );

        try {
            if ($ordre->estTermine()) {
                throw new \LogicException(
                    'Cet ordre est terminé, il n’est plus possible d’y ajouter un consommable.'
                );
            }

            $detail = $ordre->getCommandeDetail();

            if ($detail === null) {
                throw new \LogicException(
                    'Aucun détail de commande n’est associé à cet ordre.'
                );
            }

            $articleId = $request->request->getInt('article_id');
            $article = $articlesRepository->find($articleId);

            if (!$article instanceof Articles) {
                throw new \InvalidArgumentException(
                    'Veuillez sélectionner un article.'
                );
            }

            $quantite = $request->request->getInt('quantite');

            $stockService->enregistrerConsommableManuel(
                $detail,
                $article,
                $quantite,
                $ordre->getNumero()
            );

            $this->addFlash(
                'success',
                sprintf(
                    '%s retiré du stock (%d).',
                    (string) $article,
                    $quantite
                )
            );
        } catch (
            \LogicException |
            \InvalidArgumentException $e
        ) {
            $this->addFlash(
                'error',
                $e->getMessage()
            );
        }

        return $this->redirigerVersOrdre($ordre);
    }

    /**
     * Supprime un consommable enregistré par erreur : la sortie de
     * stock correspondante est annulée (le stock redevient
     * disponible).
     */
    #[Route(
        '/{id}/consommable/{sortie}/supprimer',
        name: 'supprimer_consommable',
        requirements: ['id' => '\d+', 'sortie' => '\d+'],
        methods: ['POST']
    )]
    public function supprimerConsommable(
        OrdreProduction $ordre,
        StockSorties $sortie,
        Request $request,
        StockService $stockService
    ): Response {
        $this->verifierJeton(
            $request,
            'production_supprimer_consommable_' . $sortie->getId()
        );

        try {
            if (
                $sortie->getCommandeDetail() !== $ordre->getCommandeDetail()
                || $sortie->getOrigine() !== StockSorties::ORIGINE_MANUELLE
                || $sortie->getReferenceOrigine() !== $ordre->getNumero()
            ) {
                throw new \LogicException(
                    'Ce consommable n’appartient pas à cet ordre de production.'
                );
            }

            $stockService->supprimerConsommableManuel($sortie);

            $this->addFlash(
                'success',
                'Le consommable a été retiré et le stock recrédité.'
            );
        } catch (\LogicException $e) {
            $this->addFlash(
                'error',
                $e->getMessage()
            );
        }

        return $this->redirigerVersOrdre($ordre);
    }

    /**
     * Annule un ordre non terminé.
     */"""

CTRL_BLOC_SUPPRESSION_CONSOMMABLE_NOUVEAU = r"""    /**
     * Annule un ordre non terminé.
     */"""

CTRL_MARQUEUR = "Nouvelle impression démarrée"


# ============================================================
# 2) src/Repository/OrdreProductionRepository.php
# ============================================================

REPO_BLOC_ANCIEN = r"""        ->andWhere('ordre.statut IN (:statuts)')
        ->setParameter('statuts', [
            OrdreProduction::STATUT_A_PRODUIRE,
            OrdreProduction::STATUT_EN_COURS,
            OrdreProduction::STATUT_EN_PAUSE,
        ])
        ->orderBy('ordre.creeLe', 'ASC');"""

REPO_BLOC_NOUVEAU = r"""        ->andWhere('ordre.statut IN (:statuts)')
        ->setParameter('statuts', [
            OrdreProduction::STATUT_A_PRODUIRE,
            OrdreProduction::STATUT_EN_COURS,
            OrdreProduction::STATUT_EN_PAUSE,
        ])
        ->orderBy(
            'CASE
                WHEN ordre.priorite = :prioriteUrgente THEN 0
                WHEN ordre.priorite = :prioriteHaute THEN 1
                WHEN ordre.priorite = :prioriteNormale THEN 2
                ELSE 3
            END',
            'ASC'
        )
        ->addOrderBy('ordre.creeLe', 'ASC')
        ->setParameter('prioriteUrgente', OrdreProduction::PRIORITE_URGENTE)
        ->setParameter('prioriteHaute', OrdreProduction::PRIORITE_HAUTE)
        ->setParameter('prioriteNormale', OrdreProduction::PRIORITE_NORMALE);"""

REPO_MARQUEUR = "prioriteUrgente"


# ============================================================
# 3) src/Service/StockService.php
# ============================================================

STOCK_BLOC_ANCIEN = r"""    public function enregistrerConsommableManuel(
        CommandesDetails $detail,
        Articles $article,
        int $quantite,
        string $referenceOrigine
    ): StockSorties {"""

STOCK_BLOC_NOUVEAU = r"""    public function enregistrerConsommableManuel(
        ?CommandesDetails $detail,
        Articles $article,
        int $quantite,
        ?string $referenceOrigine = null
    ): StockSorties {"""

STOCK_MARQUEUR = "?string $referenceOrigine = null"


# ============================================================
# 4) templates/production/index.html.twig
# ============================================================

INDEX_BLOC_ENTETE_ANCIEN = """\t\t\t\t\t\t\t<tr>
\t\t\t\t\t\t\t\t<th>Ordre</th>
\t\t\t\t\t\t\t\t<th>Commande</th>
\t\t\t\t\t\t\t\t<th>Priorité</th>"""

INDEX_BLOC_ENTETE_NOUVEAU = """\t\t\t\t\t\t\t<tr>
\t\t\t\t\t\t\t\t<th>Ordre</th>
\t\t\t\t\t\t\t\t<th>Commande</th>
\t\t\t\t\t\t\t\t<th>Désignation</th>
\t\t\t\t\t\t\t\t<th>Qté à imprimer</th>
\t\t\t\t\t\t\t\t<th>Priorité</th>"""

INDEX_BLOC_CELLULES_ANCIEN = """\t\t\t\t\t\t\t\t\t<td>
\t\t\t\t\t\t\t\t\t\t{% if ordre.commandeDetail
                                        and ordre.commandeDetail.commande %}
\t\t\t\t\t\t\t\t\t\t\t<strong>
\t\t\t\t\t\t\t\t\t\t\t\t#{{ ordre.commandeDetail.commande.id }}
\t\t\t\t\t\t\t\t\t\t\t</strong>
\t\t\t\t\t\t\t\t\t\t{% else %}
\t\t\t\t\t\t\t\t\t\t\t<span class="text-muted">—</span>
\t\t\t\t\t\t\t\t\t\t{% endif %}
\t\t\t\t\t\t\t\t\t</td>

\t\t\t\t\t\t\t\t\t<td>
\t\t\t\t\t\t\t\t\t\t{% if ordre.priorite == 'urgente' %}"""

INDEX_BLOC_CELLULES_NOUVEAU = """\t\t\t\t\t\t\t\t\t<td>
\t\t\t\t\t\t\t\t\t\t{% if ordre.commandeDetail
                                        and ordre.commandeDetail.commande %}
\t\t\t\t\t\t\t\t\t\t\t<strong>
\t\t\t\t\t\t\t\t\t\t\t\t#{{ ordre.commandeDetail.commande.id }}
\t\t\t\t\t\t\t\t\t\t\t</strong>
\t\t\t\t\t\t\t\t\t\t{% else %}
\t\t\t\t\t\t\t\t\t\t\t<span class="text-muted">—</span>
\t\t\t\t\t\t\t\t\t\t{% endif %}
\t\t\t\t\t\t\t\t\t</td>

\t\t\t\t\t\t\t\t\t<td>
\t\t\t\t\t\t\t\t\t\t{{ ordre.commandeDetail.designation|default('—') }}
\t\t\t\t\t\t\t\t\t</td>

\t\t\t\t\t\t\t\t\t<td>
\t\t\t\t\t\t\t\t\t\t{{ ordre.quantite|default('—') }}
\t\t\t\t\t\t\t\t\t</td>

\t\t\t\t\t\t\t\t\t<td>
\t\t\t\t\t\t\t\t\t\t{% if ordre.priorite == 'urgente' %}"""

INDEX_BLOC_RECHERCHE_ANCIEN = """\t\t\t\t\t\t\t\t{% set recherche = (
        ordre.numero ~ ' ' ~
        (
            ordre.commandeDetail
            and ordre.commandeDetail.commande
                ? ordre.commandeDetail.commande.id
                : ''
        ) ~ ' ' ~
        (
            ordre.machine
                ? ordre.machine.nom
                : ''
        ) ~ ' ' ~
        creeParTexte
    )|lower %}"""

INDEX_BLOC_RECHERCHE_NOUVEAU = """\t\t\t\t\t\t\t\t{% set recherche = (
        ordre.numero ~ ' ' ~
        (
            ordre.commandeDetail
            and ordre.commandeDetail.commande
                ? ordre.commandeDetail.commande.id
                : ''
        ) ~ ' ' ~
        (
            ordre.commandeDetail
                ? ordre.commandeDetail.designation|default('')
                : ''
        ) ~ ' ' ~
        (
            ordre.machine
                ? ordre.machine.nom
                : ''
        ) ~ ' ' ~
        creeParTexte
    )|lower %}"""

INDEX_BLOC_COLSPAN1_ANCIEN = """\t\t\t\t\t\t\t{% else %}
\t\t\t\t\t\t\t\t<tr>
\t\t\t\t\t\t\t\t\t<td colspan="9" class="text-center text-muted py-4">
\t\t\t\t\t\t\t\t\t\tAucun ordre de production disponible.
\t\t\t\t\t\t\t\t\t</td>
\t\t\t\t\t\t\t\t</tr>
\t\t\t\t\t\t\t{% endfor %}"""

INDEX_BLOC_COLSPAN1_NOUVEAU = """\t\t\t\t\t\t\t{% else %}
\t\t\t\t\t\t\t\t<tr>
\t\t\t\t\t\t\t\t\t<td colspan="11" class="text-center text-muted py-4">
\t\t\t\t\t\t\t\t\t\tAucun ordre de production disponible.
\t\t\t\t\t\t\t\t\t</td>
\t\t\t\t\t\t\t\t</tr>
\t\t\t\t\t\t\t{% endfor %}"""

INDEX_BLOC_COLSPAN2_ANCIEN = """\t\t\t\t\t\t\t<tr id="aucunResultat" style="display: none;">
\t\t\t\t\t\t\t\t<td colspan="9" class="text-center text-muted py-4">
\t\t\t\t\t\t\t\t\tAucun ordre ne correspond aux filtres.
\t\t\t\t\t\t\t\t</td>
\t\t\t\t\t\t\t</tr>"""

INDEX_BLOC_COLSPAN2_NOUVEAU = """\t\t\t\t\t\t\t<tr id="aucunResultat" style="display: none;">
\t\t\t\t\t\t\t\t<td colspan="11" class="text-center text-muted py-4">
\t\t\t\t\t\t\t\t\tAucun ordre ne correspond aux filtres.
\t\t\t\t\t\t\t\t</td>
\t\t\t\t\t\t\t</tr>"""

INDEX_MARQUEUR = "Qté à imprimer"


# ============================================================
# 5) templates/production/show.html.twig
# ============================================================

SHOW_BLOC_ANCIEN = """\t\t\t\t\t{# CONSOMMABLES DE PRODUCTION #}
\t\t\t\t\t{% if ordre.statut not in statutsTermines %}
\t\t\t\t\t\t<div class="card mb-3">
\t\t\t\t\t\t\t<div class="card-header">
\t\t\t\t\t\t\t\t<h5 class="card-title mb-0">
\t\t\t\t\t\t\t\t\tConsommables utilisés
\t\t\t\t\t\t\t\t</h5>
\t\t\t\t\t\t\t</div>

\t\t\t\t\t\t\t<div class="card-body">

\t\t\t\t\t\t\t\t{% if consommables|length > 0 %}
\t\t\t\t\t\t\t\t\t<ul class="list-group mb-3">
\t\t\t\t\t\t\t\t\t\t{% for consommable in consommables %}
\t\t\t\t\t\t\t\t\t\t\t<li class="list-group-item d-flex justify-content-between align-items-center">

\t\t\t\t\t\t\t\t\t\t\t\t<div>
\t\t\t\t\t\t\t\t\t\t\t\t\t<strong>{{ consommable.article }}</strong>
\t\t\t\t\t\t\t\t\t\t\t\t\t<span class="text-muted">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t&times; {{ consommable.quantite }}
\t\t\t\t\t\t\t\t\t\t\t\t\t</span>
\t\t\t\t\t\t\t\t\t\t\t\t</div>

\t\t\t\t\t\t\t\t\t\t\t\t<form method="post" action="{{ path( 'app_production_supprimer_consommable', {id: ordre.id, sortie: consommable.id} ) }}" class="js-confirm-form" data-message="Retirer ce consommable et recréditer le stock ?">

\t\t\t\t\t\t\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token( 'production_supprimer_consommable_' ~ consommable.id ) }}">

\t\t\t\t\t\t\t\t\t\t\t\t\t<button type="submit" class="btn btn-sm btn-danger-light" title="Retirer">
\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-times"></i>
\t\t\t\t\t\t\t\t\t\t\t\t\t</button>
\t\t\t\t\t\t\t\t\t\t\t\t</form>

\t\t\t\t\t\t\t\t\t\t\t</li>
\t\t\t\t\t\t\t\t\t\t{% endfor %}
\t\t\t\t\t\t\t\t\t</ul>
\t\t\t\t\t\t\t\t{% else %}
\t\t\t\t\t\t\t\t\t<p class="text-muted">
\t\t\t\t\t\t\t\t\t\tAucun consommable enregistré pour cet ordre.
\t\t\t\t\t\t\t\t\t</p>
\t\t\t\t\t\t\t\t{% endif %}

\t\t\t\t\t\t\t\t<form method="post" action="{{ path( 'app_production_ajouter_consommable', {id: ordre.id} ) }}">

\t\t\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token( 'production_ajouter_consommable_' ~ ordre.id ) }}">

\t\t\t\t\t\t\t\t\t<div class="form-group">
\t\t\t\t\t\t\t\t\t\t<label for="consommable_article">
\t\t\t\t\t\t\t\t\t\t\tArticle consommé
\t\t\t\t\t\t\t\t\t\t</label>

\t\t\t\t\t\t\t\t\t\t<select id="consommable_article" name="article_id" class="form-control" required>
\t\t\t\t\t\t\t\t\t\t\t<option value="">
\t\t\t\t\t\t\t\t\t\t\t\tSélectionnez un article...
\t\t\t\t\t\t\t\t\t\t\t</option>

\t\t\t\t\t\t\t\t\t\t\t{% for article in articlesConsommables %}
\t\t\t\t\t\t\t\t\t\t\t\t<option value="{{ article.id }}">
\t\t\t\t\t\t\t\t\t\t\t\t\t{{ article }}
\t\t\t\t\t\t\t\t\t\t\t\t</option>
\t\t\t\t\t\t\t\t\t\t\t{% endfor %}
\t\t\t\t\t\t\t\t\t\t</select>
\t\t\t\t\t\t\t\t\t</div>

\t\t\t\t\t\t\t\t\t<div class="form-group">
\t\t\t\t\t\t\t\t\t\t<label for="consommable_quantite">
\t\t\t\t\t\t\t\t\t\t\tQuantité
\t\t\t\t\t\t\t\t\t\t</label>

\t\t\t\t\t\t\t\t\t\t<input type="number" id="consommable_quantite" name="quantite" class="form-control" min="1" step="1" value="1" required>
\t\t\t\t\t\t\t\t\t</div>

\t\t\t\t\t\t\t\t\t<button type="submit" class="btn btn-secondary btn-block">
\t\t\t\t\t\t\t\t\t\t<i class="fa fa-minus-circle mr-1"></i>
\t\t\t\t\t\t\t\t\t\tRetirer du stock
\t\t\t\t\t\t\t\t\t</button>
\t\t\t\t\t\t\t\t</form>

\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t</div>
\t\t\t\t\t{% endif %}"""

SHOW_BLOC_NOUVEAU = """\t\t\t\t\t{# CONSOMMABLES DE PRODUCTION #}
\t\t\t\t\t{% if ordre.statut not in statutsTermines %}
\t\t\t\t\t\t<div class="card mb-3">
\t\t\t\t\t\t\t<div class="card-body">
\t\t\t\t\t\t\t\t<a href="{{ path('app_consommables_index') }}" class="btn btn-outline-secondary btn-block">
\t\t\t\t\t\t\t\t\t<i class="fa fa-minus-circle mr-1"></i>
\t\t\t\t\t\t\t\t\tEnregistrer un consommable utilisé
\t\t\t\t\t\t\t\t</a>
\t\t\t\t\t\t\t</div>
\t\t\t\t\t\t</div>
\t\t\t\t\t{% endif %}"""

SHOW_MARQUEUR = "app_consommables_index"


# ============================================================
# 6) templates/base.html.twig
# ============================================================

BASE_BLOC_MENUACTIF_ANCIEN = """\t{% elseif
\t\trouteCourante starts with 'app_production_'
\t\tor routeCourante starts with 'app_controle_pre_presse_'
\t\tor routeCourante starts with 'app_ordre_fabrication_'
\t%}

\t\t{% set menuActif = 'production' %}"""

BASE_BLOC_MENUACTIF_NOUVEAU = """\t{% elseif
\t\trouteCourante starts with 'app_production_'
\t\tor routeCourante starts with 'app_controle_pre_presse_'
\t\tor routeCourante starts with 'app_ordre_fabrication_'
\t\tor routeCourante starts with 'app_consommables_'
\t%}

\t\t{% set menuActif = 'production' %}"""

BASE_BLOC_LIEN_ANCIEN = '<a href="{{ path(\'app_production_apercu\') }}" class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tslide-item\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\trouteCourante\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t== \'app_production_apercu\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t? \'active\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t: \'\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t}}\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-eye mr-2"></i>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tVue d\'ensemble\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t{# =====================================\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t   '

BASE_BLOC_LIEN_NOUVEAU = '<a href="{{ path(\'app_production_apercu\') }}" class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tslide-item\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\trouteCourante\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t== \'app_production_apercu\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t? \'active\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t: \'\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t}}\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-eye mr-2"></i>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tVue d\'ensemble\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t{# =====================================\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t   CONSOMMABLES\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t   ===================================== #}\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t<a href="{{ path(\'app_consommables_index\') }}" class="\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tslide-item\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t{{\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\trouteCourante\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tstarts with\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\'app_consommables_\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t? \'active\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t: \'\'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t}}\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-minus-circle mr-2"></i>\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tConsommables\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t{# =====================================\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t   '


BASE_MARQUEUR = "app_consommables_"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    if not PHP_LINT_DISPONIBLE:
        print("(info : commande 'php' introuvable ici, le controle 'php -l' sera saute)")
        print()

    resultats = []

    print("-" * 70)
    print("1) src/Controller/ProductionController.php")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "src/Controller/ProductionController.php",
        CTRL_MARQUEUR,
        [
            (CTRL_BLOC_SHOW_ANCIEN, CTRL_BLOC_SHOW_NOUVEAU),
            (CTRL_BLOC_DEMARRER_SIGNATURE_ANCIEN, CTRL_BLOC_DEMARRER_SIGNATURE_NOUVEAU),
            (CTRL_BLOC_DEMARRER_CORPS_ANCIEN, CTRL_BLOC_DEMARRER_CORPS_NOUVEAU),
            (CTRL_BLOC_SUPPRESSION_CONSOMMABLE_ANCIEN, CTRL_BLOC_SUPPRESSION_CONSOMMABLE_NOUVEAU),
            (CTRL_BLOC_RECUPERER_MACHINE_ANCIEN, CTRL_BLOC_RECUPERER_MACHINE_NOUVEAU),
            (CTRL_BLOC_IMPORTS_ANCIEN, CTRL_BLOC_IMPORTS_NOUVEAU),
        ]
    ))
    print()

    print("-" * 70)
    print("2) src/Repository/OrdreProductionRepository.php")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "src/Repository/OrdreProductionRepository.php",
        REPO_MARQUEUR,
        [
            (REPO_BLOC_ANCIEN, REPO_BLOC_NOUVEAU),
        ]
    ))
    print()

    print("-" * 70)
    print("3) src/Service/StockService.php")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "src/Service/StockService.php",
        STOCK_MARQUEUR,
        [
            (STOCK_BLOC_ANCIEN, STOCK_BLOC_NOUVEAU),
        ]
    ))
    print()

    print("-" * 70)
    print("4) templates/production/index.html.twig")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "templates/production/index.html.twig",
        INDEX_MARQUEUR,
        [
            (INDEX_BLOC_ENTETE_ANCIEN, INDEX_BLOC_ENTETE_NOUVEAU),
            (INDEX_BLOC_CELLULES_ANCIEN, INDEX_BLOC_CELLULES_NOUVEAU),
            (INDEX_BLOC_RECHERCHE_ANCIEN, INDEX_BLOC_RECHERCHE_NOUVEAU),
            (INDEX_BLOC_COLSPAN1_ANCIEN, INDEX_BLOC_COLSPAN1_NOUVEAU),
            (INDEX_BLOC_COLSPAN2_ANCIEN, INDEX_BLOC_COLSPAN2_NOUVEAU),
        ]
    ))
    print()

    print("-" * 70)
    print("5) templates/production/show.html.twig")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "templates/production/show.html.twig",
        SHOW_MARQUEUR,
        [
            (SHOW_BLOC_ANCIEN, SHOW_BLOC_NOUVEAU),
        ]
    ))
    print()

    print("-" * 70)
    print("6) templates/base.html.twig")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "templates/base.html.twig",
        BASE_MARQUEUR,
        [
            (BASE_BLOC_MENUACTIF_ANCIEN, BASE_BLOC_MENUACTIF_NOUVEAU),
            (BASE_BLOC_LIEN_ANCIEN, BASE_BLOC_LIEN_NOUVEAU),
        ]
    ))
    print()

    print("-" * 70)
    print("7) src/Controller/ConsommablesController.php (nouveau fichier)")
    print("-" * 70)
    resultats.append(creer_fichier_verifie(
        racine,
        "src/Controller/ConsommablesController.php",
        CONSOMMABLES_CONTROLLER_PHP
    ))
    print()

    print("-" * 70)
    print("8) templates/consommables/index.html.twig (nouveau fichier)")
    print("-" * 70)
    resultats.append(creer_fichier_verifie(
        racine,
        "templates/consommables/index.html.twig",
        CONSOMMABLES_INDEX_TWIG
    ))
    print()

    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("- Le demarrage d'une production ne plante plus (page blanche 500).")
        print("- Les admins/ROLE_PRODUCTION recoivent une alerte a chaque")
        print("  demarrage d'impression (cloche de notifications).")
        print("- La liste de production est triee par priorite puis anciennete.")
        print("- La liste affiche desormais la designation et la quantite a")
        print("  imprimer.")
        print("- Un nouvel ecran 'Consommables' (menu Production) permet")
        print("  d'enregistrer un consommable sans passer par un ordre de")
        print("  production precis.")
    else:
        print("Au moins un fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


CONSOMMABLES_CONTROLLER_PHP = "<?php\n\nnamespace App\\Controller;\n\nuse App\\Entity\\Articles;\nuse App\\Entity\\StockSorties;\nuse App\\Repository\\ArticlesRepository;\nuse App\\Service\\StockService;\nuse Doctrine\\ORM\\EntityManagerInterface;\nuse Symfony\\Bundle\\FrameworkBundle\\Controller\\AbstractController;\nuse Symfony\\Component\\HttpFoundation\\Request;\nuse Symfony\\Component\\HttpFoundation\\Response;\nuse Symfony\\Component\\Routing\\Attribute\\Route;\n\n/**\n * Consommables de production (colle, encre, film...) : contrairement\n * à la nomenclature automatique d'un produit, un consommable manuel\n * n'est pas rattaché à un ordre de production précis. C'est un écran\n * indépendant, accessible depuis le menu, qui retire directement du\n * stock disponible.\n */\n#[Route('/consommables', name: 'app_consommables_')]\nfinal class ConsommablesController extends AbstractController\n{\n    #[Route('', name: 'index', methods: ['GET'])]\n    public function index(\n        EntityManagerInterface $em,\n        ArticlesRepository $articlesRepository\n    ): Response {\n        $consommables = $em->getRepository(StockSorties::class)->findBy(\n            ['origine' => StockSorties::ORIGINE_MANUELLE],\n            ['date' => 'DESC']\n        );\n\n        return $this->render('consommables/index.html.twig', [\n            'consommables' => $consommables,\n            'articlesConsommables' => $articlesRepository->findConsommables(),\n        ]);\n    }\n\n    #[Route('/ajouter', name: 'ajouter', methods: ['POST'])]\n    public function ajouter(\n        Request $request,\n        ArticlesRepository $articlesRepository,\n        StockService $stockService\n    ): Response {\n        $this->verifierJeton($request, 'consommables_ajouter');\n\n        try {\n            $articleId = $request->request->getInt('article_id');\n            $article = $articlesRepository->find($articleId);\n\n            if (!$article instanceof Articles) {\n                throw new \\InvalidArgumentException(\n                    'Veuillez sélectionner un article.'\n                );\n            }\n\n            $quantite = $request->request->getInt('quantite');\n\n            $reference = trim((string) $request->request->get('reference'));\n\n            $stockService->enregistrerConsommableManuel(\n                null,\n                $article,\n                $quantite,\n                $reference !== '' ? $reference : null\n            );\n\n            $this->addFlash(\n                'success',\n                sprintf(\n                    '%s retiré du stock (%d).',\n                    (string) $article,\n                    $quantite\n                )\n            );\n        } catch (\n            \\LogicException |\n            \\InvalidArgumentException $e\n        ) {\n            $this->addFlash('error', $e->getMessage());\n        }\n\n        return $this->redirectToRoute('app_consommables_index');\n    }\n\n    #[Route('/{sortie}/supprimer', name: 'supprimer', requirements: ['sortie' => '\\d+'], methods: ['POST'])]\n    public function supprimer(\n        StockSorties $sortie,\n        Request $request,\n        StockService $stockService\n    ): Response {\n        $this->verifierJeton($request, 'consommables_supprimer_' . $sortie->getId());\n\n        try {\n            if ($sortie->getOrigine() !== StockSorties::ORIGINE_MANUELLE) {\n                throw new \\LogicException(\n                    'Cette sortie de stock n’est pas un consommable manuel.'\n                );\n            }\n\n            $stockService->supprimerConsommableManuel($sortie);\n\n            $this->addFlash(\n                'success',\n                'Le consommable a été retiré et le stock recrédité.'\n            );\n        } catch (\\LogicException $e) {\n            $this->addFlash('error', $e->getMessage());\n        }\n\n        return $this->redirectToRoute('app_consommables_index');\n    }\n\n    private function verifierJeton(Request $request, string $id): void\n    {\n        $token = (string) $request->request->get('_token');\n\n        if (!$this->isCsrfTokenValid($id, $token)) {\n            throw $this->createAccessDeniedException(\n                'Jeton de sécurité invalide.'\n            );\n        }\n    }\n}\n"

CONSOMMABLES_INDEX_TWIG = '{% extends \'base.html.twig\' %}\n\n{% block title %}\n\tConsommables\n{% endblock %}\n\n{% block body %}\n\n\t{% include "alert.html.twig" %}\n\n\t<div class="side-app">\n\n\t\t<div class="page-header">\n\n\t\t\t<div>\n\t\t\t\t<h1 class="page-title">\n\t\t\t\t\tConsommables\n\t\t\t\t</h1>\n\n\t\t\t\t<ol class="breadcrumb">\n\t\t\t\t\t<li class="breadcrumb-item">\n\t\t\t\t\t\tProduction\n\t\t\t\t\t</li>\n\t\t\t\t\t<li class="breadcrumb-item active">\n\t\t\t\t\t\tConsommables\n\t\t\t\t\t</li>\n\t\t\t\t</ol>\n\t\t\t</div>\n\n\t\t</div>\n\n\t\t<div class="row row-cards">\n\n\t\t\t<div class="col-lg-5">\n\n\t\t\t\t<div class="card">\n\t\t\t\t\t<div class="card-header">\n\t\t\t\t\t\t<h5 class="card-title mb-0">\n\t\t\t\t\t\t\tEnregistrer un consommable\n\t\t\t\t\t\t</h5>\n\t\t\t\t\t</div>\n\n\t\t\t\t\t<div class="card-body">\n\n\t\t\t\t\t\t<form method="post" action="{{ path(\'app_consommables_ajouter\') }}">\n\n\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token(\'consommables_ajouter\') }}">\n\n\t\t\t\t\t\t\t<div class="form-group">\n\t\t\t\t\t\t\t\t<label for="consommable_article">\n\t\t\t\t\t\t\t\t\tArticle consommé\n\t\t\t\t\t\t\t\t</label>\n\n\t\t\t\t\t\t\t\t<select id="consommable_article" name="article_id" class="form-control" required>\n\t\t\t\t\t\t\t\t\t<option value="">\n\t\t\t\t\t\t\t\t\t\tSélectionnez un article...\n\t\t\t\t\t\t\t\t\t</option>\n\n\t\t\t\t\t\t\t\t\t{% for article in articlesConsommables %}\n\t\t\t\t\t\t\t\t\t\t<option value="{{ article.id }}">\n\t\t\t\t\t\t\t\t\t\t\t{{ article }}\n\t\t\t\t\t\t\t\t\t\t</option>\n\t\t\t\t\t\t\t\t\t{% endfor %}\n\t\t\t\t\t\t\t\t</select>\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t<div class="form-group">\n\t\t\t\t\t\t\t\t<label for="consommable_quantite">\n\t\t\t\t\t\t\t\t\tQuantité\n\t\t\t\t\t\t\t\t</label>\n\n\t\t\t\t\t\t\t\t<input type="number" id="consommable_quantite" name="quantite" class="form-control" min="1" step="1" value="1" required>\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t<div class="form-group">\n\t\t\t\t\t\t\t\t<label for="consommable_reference">\n\t\t\t\t\t\t\t\t\tRéférence (facultatif)\n\t\t\t\t\t\t\t\t</label>\n\n\t\t\t\t\t\t\t\t<input type="text" id="consommable_reference" name="reference" class="form-control" placeholder="Ex : commande #123, nettoyage machine...">\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t<button type="submit" class="btn btn-secondary btn-block">\n\t\t\t\t\t\t\t\t<i class="fa fa-minus-circle mr-1"></i>\n\t\t\t\t\t\t\t\tRetirer du stock\n\t\t\t\t\t\t\t</button>\n\t\t\t\t\t\t</form>\n\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\n\t\t\t</div>\n\n\t\t\t<div class="col-lg-7">\n\n\t\t\t\t<div class="card">\n\t\t\t\t\t<div class="card-header">\n\t\t\t\t\t\t<div>\n\t\t\t\t\t\t\t<h5 class="card-title mb-1">\n\t\t\t\t\t\t\t\tHistorique des consommables\n\t\t\t\t\t\t\t</h5>\n\t\t\t\t\t\t\t<small class="text-muted">\n\t\t\t\t\t\t\t\t{{ consommables|length }} enregistrement(s)\n\t\t\t\t\t\t\t</small>\n\t\t\t\t\t\t</div>\n\t\t\t\t\t</div>\n\n\t\t\t\t\t<div class="card-body p-0">\n\t\t\t\t\t\t{% if consommables|length > 0 %}\n\t\t\t\t\t\t\t<ul class="list-group list-group-flush">\n\t\t\t\t\t\t\t\t{% for consommable in consommables %}\n\t\t\t\t\t\t\t\t\t<li class="list-group-item d-flex justify-content-between align-items-center">\n\n\t\t\t\t\t\t\t\t\t\t<div>\n\t\t\t\t\t\t\t\t\t\t\t<strong>{{ consommable.article }}</strong>\n\t\t\t\t\t\t\t\t\t\t\t<span class="text-muted">\n\t\t\t\t\t\t\t\t\t\t\t\t&times; {{ consommable.quantite }}\n\t\t\t\t\t\t\t\t\t\t\t</span>\n\n\t\t\t\t\t\t\t\t\t\t\t<div class="small text-muted">\n\t\t\t\t\t\t\t\t\t\t\t\t{{ consommable.date ? consommable.date|date(\'d/m/Y H:i\') : \'\' }}\n\n\t\t\t\t\t\t\t\t\t\t\t\t{% if consommable.referenceOrigine %}\n\t\t\t\t\t\t\t\t\t\t\t\t\t— {{ consommable.referenceOrigine }}\n\t\t\t\t\t\t\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t\t\t<form method="post" action="{{ path(\'app_consommables_supprimer\', {sortie: consommable.id}) }}" class="js-confirm-form" data-message="Retirer ce consommable et recréditer le stock ?">\n\n\t\t\t\t\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token(\'consommables_supprimer_\' ~ consommable.id) }}">\n\n\t\t\t\t\t\t\t\t\t\t\t<button type="submit" class="btn btn-sm btn-danger-light" title="Retirer">\n\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-times"></i>\n\t\t\t\t\t\t\t\t\t\t\t</button>\n\t\t\t\t\t\t\t\t\t\t</form>\n\n\t\t\t\t\t\t\t\t\t</li>\n\t\t\t\t\t\t\t\t{% endfor %}\n\t\t\t\t\t\t\t</ul>\n\t\t\t\t\t\t{% else %}\n\t\t\t\t\t\t\t<p class="text-muted text-center py-4 mb-0">\n\t\t\t\t\t\t\t\tAucun consommable enregistré.\n\t\t\t\t\t\t\t</p>\n\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\n\t\t\t</div>\n\n\t\t</div>\n\n\t</div>\n\n{% endblock %}\n'


if __name__ == "__main__":
    main()
