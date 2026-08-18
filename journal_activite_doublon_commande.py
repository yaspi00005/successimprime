"""
Trace dans le Journal d'activité les tentatives de doublon bloquées
lors de l'enregistrement d'une commande.

- La création normale d'une commande est DÉJÀ tracée automatiquement
  par App\\EventSubscriber\\AuditSubscriber (Commandes::class y figure
  déjà dans ENTITES_SUIVIES). Rien à faire de ce côté.
- En revanche, quand un doublon est détecté, on quitte AVANT le
  persist/flush : cette tentative ne laisse donc aucune trace. Ce
  script ajoute une entrée explicite dans le journal à ce moment-là.

À exécuter à la racine du dépôt : python3 journal_activite_doublon_commande.py
"""

import sys


def appliquer(path, old, new, label):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if new in content:
        print(f"[SKIP] {label} : déjà présent dans {path}")
        return

    count = content.count(old)
    if count != 1:
        print(f"[ERREUR] {label} : {count} occurrence(s) trouvée(s) dans {path} (1 attendue)")
        sys.exit(1)

    content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] {label} appliqué à {path}")


# ------------------------------------------------------------------
# 1) src/Entity/JournalActivite.php : nouvelle constante d'action
# ------------------------------------------------------------------
appliquer(
    "src/Entity/JournalActivite.php",
    """    public const ACTION_CREATION = 'creation';
    public const ACTION_MODIFICATION = 'modification';
    public const ACTION_SUPPRESSION = 'suppression';""",
    """    public const ACTION_CREATION = 'creation';
    public const ACTION_MODIFICATION = 'modification';
    public const ACTION_SUPPRESSION = 'suppression';
    public const ACTION_DOUBLON_BLOQUE = 'doublon_bloque';""",
    "Constante ACTION_DOUBLON_BLOQUE",
)

# ------------------------------------------------------------------
# 2) templates/journal_activite/index.html.twig : filtre + badge
# ------------------------------------------------------------------
appliquer(
    "templates/journal_activite/index.html.twig",
    """						<option value="creation" {{ filtres.action == 'creation' ? 'selected' : '' }}>Création</option>
							<option value="modification" {{ filtres.action == 'modification' ? 'selected' : '' }}>Modification</option>
							<option value="suppression" {{ filtres.action == 'suppression' ? 'selected' : '' }}>Suppression</option>""",
    """						<option value="creation" {{ filtres.action == 'creation' ? 'selected' : '' }}>Création</option>
							<option value="modification" {{ filtres.action == 'modification' ? 'selected' : '' }}>Modification</option>
							<option value="suppression" {{ filtres.action == 'suppression' ? 'selected' : '' }}>Suppression</option>
							<option value="doublon_bloque" {{ filtres.action == 'doublon_bloque' ? 'selected' : '' }}>Doublon bloqué</option>""",
    "Option de filtre 'Doublon bloqué'",
)

appliquer(
    "templates/journal_activite/index.html.twig",
    """								{% if journal.action == 'creation' %}
										<span class="badge badge-success">Création</span>
									{% elseif journal.action == 'suppression' %}
										<span class="badge badge-danger">Suppression</span>
									{% else %}
										<span class="badge badge-warning">Modification</span>
									{% endif %}""",
    """								{% if journal.action == 'creation' %}
										<span class="badge badge-success">Création</span>
									{% elseif journal.action == 'suppression' %}
										<span class="badge badge-danger">Suppression</span>
									{% elseif journal.action == 'doublon_bloque' %}
										<span class="badge badge-info">Doublon bloqué</span>
									{% else %}
										<span class="badge badge-warning">Modification</span>
									{% endif %}""",
    "Badge 'Doublon bloqué'",
)

# ------------------------------------------------------------------
# 3) src/Controller/CommandesController.php : log de la tentative
# ------------------------------------------------------------------
appliquer(
    "src/Controller/CommandesController.php",
    """                    if ($doublon !== null) {
                        $this->addFlash(
                            'warning',
                            sprintf(
                                'Cette commande semble déjà avoir été enregistrée à l’instant (commande %s). Pour éviter un doublon, elle n’a pas été enregistrée une seconde fois.',
                                $doublon->getNumero()
                                    ?? ('CMD-' . $doublon->getId())
                            )
                        );

                        return $this->redirectToRoute(
                            'app_commandes_show',
                            ['id' => $doublon->getId()],
                            Response::HTTP_SEE_OTHER
                        );
                    }""",
    """                    if ($doublon !== null) {
                        /*
                     * ================================================
                     * JOURNAL D'ACTIVITÉ
                     * ================================================
                     *
                     * La création est refusée avant tout persist, donc
                     * l'audit automatique (AuditSubscriber) ne voit
                     * jamais passer cette tentative. On la trace donc
                     * explicitement pour garder une trace de qui a
                     * tenté d'enregistrer un doublon, quand et sur
                     * quelle commande d'origine.
                     */
                        $journal = new \\App\\Entity\\JournalActivite();
                        $journal
                            ->setEntite('Commandes')
                            ->setEntiteId($doublon->getId())
                            ->setAction(\\App\\Entity\\JournalActivite::ACTION_DOUBLON_BLOQUE)
                            ->setDonneesApres([
                                'commandeOrigineId' => $doublon->getId(),
                                'commandeOrigineNumero' => $doublon->getNumero(),
                                'clientId' => $commande->getClients()?->getId(),
                                'totalTtc' => $commande->getTotalTtc(),
                            ])
                            ->setUtilisateur($utilisateur);

                        $entityManager->persist($journal);
                        $entityManager->flush();

                        $this->addFlash(
                            'warning',
                            sprintf(
                                'Cette commande semble déjà avoir été enregistrée à l’instant (commande %s). Pour éviter un doublon, elle n’a pas été enregistrée une seconde fois.',
                                $doublon->getNumero()
                                    ?? ('CMD-' . $doublon->getId())
                            )
                        );

                        return $this->redirectToRoute(
                            'app_commandes_show',
                            ['id' => $doublon->getId()],
                            Response::HTTP_SEE_OTHER
                        );
                    }""",
    "Log du doublon bloqué dans le journal d'activité",
)

print("\nTerminé.")
