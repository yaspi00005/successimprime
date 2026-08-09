<?php

namespace App\Form;

use App\Entity\CompteTresorerie;
use App\Entity\MouvementTresorerie;
use App\Repository\CompteTresorerieRepository;
use Doctrine\ORM\QueryBuilder;
use Symfony\Bridge\Doctrine\Form\Type\EntityType;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Symfony\Component\Form\Extension\Core\Type\DateTimeType;
use Symfony\Component\Form\Extension\Core\Type\IntegerType;
use Symfony\Component\Form\Extension\Core\Type\TextareaType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;
use Symfony\Component\Validator\Constraints as Assert;
use Symfony\Component\Form\FormEvent;
use Symfony\Component\Form\FormEvents;
use Symfony\Component\Form\CallbackTransformer;

class MouvementTresorerieType extends AbstractType
{
    public function buildForm(
        FormBuilderInterface $builder,
        array $options
    ): void {
        
        $queryBuilderComptesActifs = static function (
            CompteTresorerieRepository $repository
        ): QueryBuilder {
            return $repository
                ->createQueryBuilder('compte')
                ->andWhere('compte.actif = :actif')
                ->setParameter('actif', true)
                ->orderBy('compte.nom', 'ASC');
        };

        $builder
            ->add('type', ChoiceType::class, [
                'label' => 'Type de mouvement',
                'choices' => MouvementTresorerie::getTypesPourFormulaire(),
                'placeholder' => 'Sélectionner le type',
                'attr' => [
                    'class' => 'form-select',
                    'data-mouvement-type' => 'true',
                ],
            ])

            ->add('compteSource', EntityType::class, [
                'label' => 'Compte source',
                'class' => CompteTresorerie::class,
                'choice_label' => static function (
                    CompteTresorerie $compte
                ): string {
                    return sprintf(
                        '%s — %s FCFA',
                        $compte->getNom(),
                        number_format(
                            $compte->getSoldeActuel(),
                            0,
                            ',',
                            ' '
                        )
                    );
                },
                'query_builder' => $queryBuilderComptesActifs,
                'placeholder' => 'Sélectionner le compte à débiter',
                'required' => false,
                'attr' => [
                    'class' => 'form-select',
                ],
                'row_attr' => [
                    'data-compte-source-row' => 'true',
                ],
            ])

            ->add('compteDestination', EntityType::class, [
                'label' => 'Compte destination',
                'class' => CompteTresorerie::class,
                'choice_label' => static function (
                    CompteTresorerie $compte
                ): string {
                    return sprintf(
                        '%s — %s FCFA',
                        $compte->getNom(),
                        number_format(
                            $compte->getSoldeActuel(),
                            0,
                            ',',
                            ' '
                        )
                    );
                },
                'query_builder' => $queryBuilderComptesActifs,
                'placeholder' => 'Sélectionner le compte à créditer',
                'required' => false,
                'attr' => [
                    'class' => 'form-select',
                ],
                'row_attr' => [
                    'data-compte-destination-row' => 'true',
                ],
            ])

           ->add('montant', TextType::class, [
    'label' => 'Montant de l’opération',
    'attr' => [
        'class' => 'form-control montant-input',
        'inputmode' => 'numeric',
        'autocomplete' => 'off',
        'placeholder' => 'Exemple : 25 000',
        'data-montant' => 'true',
    ],
    'help' => 'Saisissez uniquement un montant entier en FCFA.',
    'constraints' => [
        new Assert\NotBlank(
            message: 'Veuillez saisir le montant de l’opération.'
        ),
        new Assert\Regex(
            pattern: '/^[0-9\s]+$/',
            message: 'Le montant doit contenir uniquement des chiffres.'
        ),
    ],
])

            ->add('devise', ChoiceType::class, [
                'label' => 'Devise',
                'choices' => [
                    'Franc CFA (XOF)' => 'XOF',
                ],
                'attr' => [
                    'class' => 'form-select',
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
                    'Chèque' => 'cheque',
                    'Carte bancaire' => 'carte_bancaire',
                    'Autre' => 'autre',
                ],
                'attr' => [
                    'class' => 'form-select',
                ],
            ])

            ->add('referenceExterne', TextType::class, [
                'label' => 'Référence externe',
                'required' => false,
                'help' => 'Numéro de transaction, reçu, chèque ou virement.',
                'attr' => [
                    'class' => 'form-control',
                    'maxlength' => 100,
                    'placeholder' => 'Exemple : transaction OM123456',
                ],
            ])

            ->add('libelle', TextType::class, [
                'label' => 'Libellé',
                'attr' => [
                    'class' => 'form-control',
                    'maxlength' => 255,
                    'placeholder' => 'Motif principal du mouvement',
                ],
            ])

            ->add('dateOperation', DateTimeType::class, [
                'label' => 'Date de l’opération',
                'widget' => 'single_text',
                'input' => 'datetime_immutable',
                'attr' => [
                    'class' => 'form-control',
                ],
            ])

            ->add('description', TextareaType::class, [
                'label' => 'Description ou observation',
                'required' => false,
                'attr' => [
                    'class' => 'form-control',
                    'rows' => 4,
                    'placeholder' => 'Informations complémentaires',
                ],
            ])
            ;
        $builder->get('montant')->addModelTransformer(
        new CallbackTransformer(
            static function ($montant): string {
                if ($montant === null || $montant === '') {
                    return '';
                }

                return number_format((int) $montant, 0, ',', ' ');
            },
            static function ($montant): ?int {
                if (
                    $montant === null
                    || trim((string) $montant) === ''
                ) {
                    return null;
                }

                $montantNettoye = preg_replace(
                    '/[^\d]/',
                    '',
                    (string) $montant
                );

                if ($montantNettoye === '') {
                    return null;
                }

                return (int) $montantNettoye;
            }
        )
    );    
    }

    public function configureOptions(
        OptionsResolver $resolver
    ): void {
        $resolver->setDefaults([
            'data_class' => MouvementTresorerie::class,
        ]);
    }
}