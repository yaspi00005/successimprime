<?php

namespace App\Form;

use App\Entity\CompteTresorerie;
use App\Entity\MouvementTresorerie;
use App\Repository\CompteTresorerieRepository;
use Doctrine\ORM\QueryBuilder;
use Symfony\Bridge\Doctrine\Form\Type\EntityType;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\Validator\Constraints as Assert;

/**
 * Formulaire (non lié à une entité) utilisé par la caisse pour payer
 * une réclamation validée : choix du compte à débiter et de la
 * catégorie financière du décaissement qui sera créé.
 */
class ReclamationPaiementType extends AbstractType
{
    public function buildForm(
        FormBuilderInterface $builder,
        array $options
    ): void {
        $builder
            ->add('compteSource', EntityType::class, [
                'label' => 'Compte à débiter',
                'class' => CompteTresorerie::class,
                'query_builder' => static function (
                    CompteTresorerieRepository $repository
                ): QueryBuilder {
                    return $repository->createQueryBuilder('compte')
                        ->andWhere('compte.actif = :actif')
                        ->setParameter('actif', true)
                        ->orderBy('compte.type', 'ASC')
                        ->addOrderBy('compte.nom', 'ASC');
                },
                'choice_label' => static function (CompteTresorerie $compte): string {
                    return sprintf(
                        '%s — %s — %s FCFA',
                        $compte->getNom(),
                        $compte->getTypeLabel(),
                        number_format((int) $compte->getSoldeActuel(), 0, ',', ' ')
                    );
                },
                'placeholder' => 'Sélectionner le compte à débiter',
                'attr' => ['class' => 'form-select'],
                'constraints' => [
                    new Assert\NotNull(message: 'Sélectionnez le compte à débiter.'),
                ],
            ])

            ->add('categorie', ChoiceType::class, [
                'label' => 'Catégorie financière',
                'choices' => MouvementTresorerie::getCategoriesPourFormulaire(),
                'data' => MouvementTresorerie::CATEGORIE_ACHAT,
                'attr' => ['class' => 'form-select'],
                'constraints' => [
                    new Assert\NotBlank(message: 'Veuillez sélectionner une catégorie financière.'),
                ],
            ])

            ->add('modePaiement', ChoiceType::class, [
                'label' => 'Mode de paiement',
                'placeholder' => 'Sélectionner le mode',
                'required' => false,
                'choices' => [
                    'Espèces' => 'especes',
                    'Orange Money' => 'orange_money',
                    'Wave' => 'wave',
                    'Virement bancaire' => 'virement',
                ],
                'attr' => ['class' => 'form-select'],
            ])
        ;
    }
}
