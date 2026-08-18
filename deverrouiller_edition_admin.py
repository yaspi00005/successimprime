"""
Permet à un administrateur de réellement modifier une commande
verrouillée (production ou livraison déjà commencée), avec une
mention "Modifié le ... par ..." affichée sur la commande.

Contexte : le contrôleur (CommandesController::edit()) autorisait
déjà un ROLE_ADMIN à accéder à l'édition d'une commande verrouillée,
mais le FORMULAIRE lui-même restait verrouillé visuellement (variable
Twig commandeVerrouillee ne tenait pas compte du rôle) : l'accès
autorisé ne servait donc à rien, tous les champs restaient bloqués.

Le journal d'activité n'a besoin d'aucun code supplémentaire : il
est déjà alimenté automatiquement par App\\EventSubscriber\\
AuditSubscriber (un "trigger" au niveau Doctrine), qui capture toute
modification de Commandes avec l'utilisateur connecté et le détail
avant/après de chaque champ, dès qu'un flush() a lieu.

Modifie :
- src/Entity/Commandes.php (champs modifieLe / modifiePar)
- src/Controller/CommandesController.php (les renseigne à l'édition)
- templates/commandes/_form.html.twig (déverrouille le formulaire
  pour l'admin)
- templates/commandes/show.html.twig (affiche "Modifié le ... par ...")

Une migration séparée (Version20260818140000.php) accompagne ce
script pour ajouter les colonnes en base.

A executer a la racine du dépôt : python3 deverrouiller_edition_admin.py
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


# ==================================================================
# 1) src/Entity/Commandes.php
# ==================================================================
ENTITE = "src/Entity/Commandes.php"

appliquer(
    ENTITE,
    """    #[ORM\\Column(type: Types::DATETIME_IMMUTABLE, nullable: true)]
    private ?\\DateTimeInterface $dateLivraison = null;""",
    """    #[ORM\\Column(type: Types::DATETIME_IMMUTABLE, nullable: true)]
    private ?\\DateTimeInterface $dateLivraison = null;

    /*
     * Dernière modification (y compris une modification d'une
     * commande normalement verrouillée, faite par un administrateur).
     */
    #[ORM\\Column(type: Types::DATETIME_IMMUTABLE, nullable: true)]
    private ?\\DateTimeInterface $modifieLe = null;

    #[ORM\\ManyToOne]
    #[ORM\\JoinColumn(nullable: true, onDelete: 'SET NULL')]
    private ?User $modifiePar = null;""",
    "Champs modifieLe / modifiePar",
)

appliquer(
    ENTITE,
    """    public function setDateLivraison(
        ?\\DateTimeInterface $dateLivraison
    ): static {
        $this->dateLivraison = $dateLivraison;

        return $this;
    }

    public function getRemise(): int""",
    """    public function setDateLivraison(
        ?\\DateTimeInterface $dateLivraison
    ): static {
        $this->dateLivraison = $dateLivraison;

        return $this;
    }

    public function getModifieLe(): ?\\DateTimeImmutable
    {
        return $this->modifieLe;
    }

    public function setModifieLe(
        ?\\DateTimeInterface $modifieLe
    ): static {
        $this->modifieLe = $modifieLe;

        return $this;
    }

    public function getModifiePar(): ?User
    {
        return $this->modifiePar;
    }

    public function setModifiePar(?User $modifiePar): static
    {
        $this->modifiePar = $modifiePar;

        return $this;
    }

    public function getRemise(): int""",
    "Getters/setters modifieLe / modifiePar",
)


# ==================================================================
# 2) src/Controller/CommandesController.php
# ==================================================================
CONTROLLER = "src/Controller/CommandesController.php"

appliquer(
    CONTROLLER,
    """                /*
             * ========================================================
             * ENREGISTREMENT
             * ========================================================
             */
                $entityManager->flush();


                $this->addFlash(
                    'success',
                    'La commande a été modifiée avec succès.'
                );""",
    """                /*
             * ========================================================
             * ENREGISTREMENT
             * ========================================================
             */
                $commande
                    ->setModifieLe(new \\DateTimeImmutable())
                    ->setModifiePar($user);

                $entityManager->flush();


                $this->addFlash(
                    'success',
                    'La commande a été modifiée avec succès.'
                );""",
    "Renseigne modifieLe/modifiePar à l'enregistrement",
)


# ==================================================================
# 3) templates/commandes/_form.html.twig
# ==================================================================
TPL_FORM = "templates/commandes/_form.html.twig"

appliquer(
    TPL_FORM,
    """{% set commandeVerrouillee =
    circuitDejaCommence|default(false)
%}""",
    """{#
    Une commande dont le circuit a déjà commencé (production ou
    livraison) est normalement verrouillée. Le contrôleur autorise
    déjà un administrateur à accéder à l'édition dans ce cas (voir
    CommandesController::edit()) : le formulaire doit donc rester
    modifiable pour lui, sinon l'accès autorisé ne sert à rien
    (tous les champs restent bloqués visuellement).
#}
{% set commandeVerrouillee =
    circuitDejaCommence|default(false)
    and not is_granted('ROLE_ADMIN')
%}""",
    "Déverrouillage du formulaire pour l'admin",
)


# ==================================================================
# 4) templates/commandes/show.html.twig
# ==================================================================
TPL_SHOW = "templates/commandes/show.html.twig"

appliquer(
    TPL_SHOW,
    """				<li class="breadcrumb-item active" aria-current="page">
					{{ reference }}
				</li>

			</ol>""",
    """				<li class="breadcrumb-item active" aria-current="page">
					{{ reference }}
				</li>

			</ol>

			{% if commande.modifieLe %}
				<div class="text-muted small mb-2">
					<i class="fe fe-edit-2 mr-1"></i>
					Modifié le {{ commande.modifieLe|date('d/m/Y à H:i') }}
					{% if commande.modifiePar %}
						par {{ commande.modifiePar.username }}
					{% endif %}
				</div>
			{% endif %}""",
    "Mention 'Modifié le ... par ...'",
)

print("\nTerminé.")
print("N'oublie pas d'exécuter aussi la migration :")
print("  php bin/console doctrine:migrations:migrate")
