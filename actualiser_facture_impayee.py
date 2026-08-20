/Users/yayadiallo/Downloads/livraison_dimension_remise_agent_session_b2b.py"""
Ajoute un bouton "Actualiser depuis la commande" sur une facture,
tant qu'elle n'est pas totalement payee.

La facture reste un instantane fige de la commande au moment de sa
creation (comportement volontaire, inchange). Ce bouton permet de
reprendre manuellement les montants ACTUELS de la commande liee
(remise, TVA, totaux...) si elle a change apres coup - via la
methode Factures::chargerDepuisCommande() qui existait deja mais
n'etait utilisee qu'a la creation. Les paiements deja enregistres
ne sont jamais modifies. Des que la facture est totalement payee
(ou annulee), le bouton disparait et l'action est refusee cote
serveur.

Le journal d'activite n'a besoin d'aucun code supplementaire :
Factures fait deja partie des entites suivies par AuditSubscriber,
qui capture automatiquement cette modification (utilisateur, avant/
apres) des le flush().

Modifie :
- src/Controller/FacturesController.php
- templates/factures/show.html.twig

A executer a la racine du depot : python3 actualiser_facture_impayee.py
"""

import sys


def appliquer(path, old, new, label):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if new in content:
        print(f"[SKIP] {label} : deja present dans {path}")
        return

    count = content.count(old)
    if count != 1:
        print(f"[ERREUR] {label} : {count} occurrence(s) trouvee(s) dans {path} (1 attendue)")
        sys.exit(1)

    content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] {label} applique a {path}")


CTRL = "src/Controller/FacturesController.php"
TPL = "templates/factures/show.html.twig"

appliquer(CTRL, "    #[Route(\n        '/{id}/annuler',", "    #[Route(\n        '/{id}/actualiser',\n        name: 'app_factures_actualiser',\n        methods: ['POST']\n    )]\n    public function actualiser(\n        Factures $facture,\n        Request $request,\n        EntityManagerInterface $entityManager\n    ): Response {\n        if (\n            !$this->isCsrfTokenValid(\n                'actualiser-facture-'\n                    . $facture->getId(),\n                (string) $request\n                    ->request\n                    ->get('_token')\n            )\n        ) {\n            throw $this\n                ->createAccessDeniedException(\n                    'Jeton CSRF invalide.'\n                );\n        }\n\n\n        if ($facture->estAnnulee()) {\n            $this->addFlash(\n                'warning',\n                'Ce document est annulé, il ne peut plus être actualisé.'\n            );\n\n            return $this->redirectToRoute(\n                'app_factures_show',\n                [\n                    'id' =>\n                    $facture->getId(),\n                ]\n            );\n        }\n\n\n        /*\n         * Une fois la facture totalement payée, elle redevient un\n         * document figé (comme à l'émission) : plus de mise à jour\n         * possible, seul un avoir permettrait de la corriger.\n         */\n        if (\n            $facture->getMontantPaye()\n            >= $facture->getTotalTtc()\n        ) {\n            $this->addFlash(\n                'warning',\n                'Cette facture est totalement payée, elle ne peut plus être actualisée.'\n            );\n\n            return $this->redirectToRoute(\n                'app_factures_show',\n                [\n                    'id' =>\n                    $facture->getId(),\n                ]\n            );\n        }\n\n\n        $commande = $facture->getCommande();\n\n        if ($commande === null) {\n            $this->addFlash(\n                'warning',\n                'Aucune commande liée à ce document, impossible de l’actualiser.'\n            );\n\n            return $this->redirectToRoute(\n                'app_factures_show',\n                [\n                    'id' =>\n                    $facture->getId(),\n                ]\n            );\n        }\n\n\n        $facture->chargerDepuisCommande($commande);\n\n        $entityManager->flush();\n\n\n        $this->addFlash(\n            'success',\n            sprintf(\n                '%s a été actualisé avec les montants actuels de la commande.',\n                $facture->getNumero()\n                    ?? 'Le document'\n            )\n        );\n\n\n        return $this->redirectToRoute(\n            'app_factures_show',\n            [\n                'id' =>\n                $facture->getId(),\n            ]\n        );\n    }\n\n    #[Route(\n        '/{id}/annuler',", "Action actualiser() + route")

appliquer(TPL, 'Synchroniser les paiements\n\n\t\t\t\t\t\t\t\t</button>\n\n\t\t\t\t\t\t\t</form>\n\n\t\t\t\t\t\t{% endif %}', 'Synchroniser les paiements\n\n\t\t\t\t\t\t\t\t</button>\n\n\t\t\t\t\t\t\t</form>\n\n\t\t\t\t\t\t{% endif %}\n\n\n\t\t\t\t\t\t{# ACTUALISATION DES MONTANTS :\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t                           TANT QUE LA FACTURE N\'EST PAS TOTALEMENT PAYÉE #}\n\n\t\t\t\t\t\t{% if\n                            facture.comptabilisee\n                            and not facture.estAnnulee\n                            and commande\n                            and facture.montantPaye < facture.totalTtc\n                        %}\n\n\t\t\t\t\t\t\t<button type="button" class="btn btn-outline-primary btn-block mb-3" id="btn-actualiser-facture">\n\n\t\t\t\t\t\t\t\t<i class="fa fa-refresh mr-1"></i>\n\n\t\t\t\t\t\t\t\tActualiser depuis la commande\n\n\t\t\t\t\t\t\t</button>\n\n\n\t\t\t\t\t\t\t<form id="form-actualiser-facture" method="post" action="{{ path( \'app_factures_actualiser\', { id: facture.id } ) }}" class="d-none">\n\n\t\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token( \'actualiser-facture-\' ~ facture.id ) }}">\n\n\t\t\t\t\t\t\t</form>\n\n\t\t\t\t\t\t{% endif %}\n\n\n\t\t\t\t\t\t', "Bouton 'Actualiser depuis la commande'")

appliquer(TPL, "const button = document.getElementById('btn-annuler-facture');\n\nconst form = document.getElementById('form-annuler-facture');\n\n\nif (! button || ! form) {\nreturn;\n}", "const boutonActualiser = document.getElementById('btn-actualiser-facture');\n\nconst formActualiser = document.getElementById('form-actualiser-facture');\n\n\nif (boutonActualiser && formActualiser) {\n\nboutonActualiser.addEventListener('click', function () {\n\nif (typeof Swal !== 'undefined') {\n\nSwal.fire({\nicon: 'question',\ntitle: 'Actualiser cette facture ?',\ntext: 'Les montants seront repris depuis la commande liée (les paiements déjà enregistrés ne sont pas modifiés).',\nshowCancelButton: true,\nconfirmButtonText: 'Oui, actualiser',\ncancelButtonText: 'Fermer'\n}).then(function (result) {\nif (result.isConfirmed) {\nformActualiser.submit();\n}\n});\n\nreturn;\n}\n\nformActualiser.submit();\n});\n}\n\n\nconst button = document.getElementById('btn-annuler-facture');\n\nconst form = document.getElementById('form-annuler-facture');\n\n\nif (! button || ! form) {\nreturn;\n}", "JS : confirmation + soumission du bouton Actualiser")

print("\nTermine.")
