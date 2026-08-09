<?php

namespace App\Form;

use App\Entity\CompteTresorerie;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\CheckboxType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Symfony\Component\Form\Extension\Core\Type\IntegerType;
use Symfony\Component\Form\Extension\Core\Type\TextareaType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class CompteTresorerieType extends AbstractType
{
    public function buildForm(
        FormBuilderInterface $builder,
        array $options
    ): void {
        /** @var CompteTresorerie|null $compte */
        $compte = $builder->getData();
        $estModification = $compte?->getId() !== null;

        $builder
            ->add('code', TextType::class, [
                'label' => 'Code du compte',
                'attr' => [
                    'class' => 'form-control',
                    'placeholder' => 'Ex. CAISSE-PRINCIPALE',
                    'maxlength' => 50,
                ],
                'help' => 'Le code sera automatiquement enregistré en majuscules.',
            ])

            ->add('nom', TextType::class, [
                'label' => 'Nom du compte',
                'attr' => [
                    'class' => 'form-control',
                    'placeholder' => 'Ex. Caisse principale',
                    'maxlength' => 150,
                ],
            ])

            ->add('type', ChoiceType::class, [
                'label' => 'Type de compte',
                'choices' => CompteTresorerie::getTypesPourFormulaire(),
                'placeholder' => 'Sélectionner un type',
                'attr' => [
                    'class' => 'form-control',
                    'data-role' => 'compte-type',
                ],
            ])

            ->add('nomBanque', TextType::class, [
                'label' => 'Nom de la banque',
                'required' => false,
                'attr' => [
                    'class' => 'form-control',
                    'placeholder' => 'Ex. BDM-SA, BOA, Ecobank',
                    'maxlength' => 150,
                ],
                'row_attr' => [
                    'class' => 'champ-bancaire',
                ],
            ])

            ->add('numeroCompte', TextType::class, [
                'label' => 'Numéro du compte ou du portefeuille',
                'required' => false,
                'attr' => [
                    'class' => 'form-control',
                    'placeholder' => 'Numéro de compte, Orange Money ou Wave',
                    'maxlength' => 100,
                ],
            ])

            ->add('titulaireCompte', TextType::class, [
                'label' => 'Titulaire du compte',
                'required' => false,
                'attr' => [
                    'class' => 'form-control',
                    'placeholder' => 'Nom du titulaire',
                    'maxlength' => 150,
                ],
            ])

            ->add('soldeInitial', IntegerType::class, [
                'label' => 'Solde initial',
                'disabled' => $estModification,
                'required' => true,
                'attr' => [
                    'class' => 'form-control',
                    'min' => 0,
                    'step' => 1,
                    'placeholder' => '0',
                ],
                'help' => $estModification
                    ? 'Le solde initial ne peut plus être modifié.'
                    : 'Montant disponible lors de la création du compte.',
            ])

            ->add('devise', ChoiceType::class, [
                'label' => 'Devise',
                'choices' => [
                    'Franc CFA (XOF)' => 'XOF',
                    'Euro (EUR)' => 'EUR',
                    'Dollar américain (USD)' => 'USD',
                ],
                'attr' => [
                    'class' => 'form-control',
                ],
            ])

            ->add('autoriserDecouvert', CheckboxType::class, [
                'label' => 'Autoriser le découvert',
                'required' => false,
                'attr' => [
                    'class' => 'custom-control-input',
                ],
                'label_attr' => [
                    'class' => 'custom-control-label',
                ],
                'row_attr' => [
                    'class' => 'custom-control custom-checkbox mb-3',
                ],
            ])

            ->add('actif', CheckboxType::class, [
                'label' => 'Compte actif',
                'required' => false,
                'attr' => [
                    'class' => 'custom-control-input',
                ],
                'label_attr' => [
                    'class' => 'custom-control-label',
                ],
                'row_attr' => [
                    'class' => 'custom-control custom-checkbox mb-3',
                ],
            ])

            ->add('description', TextareaType::class, [
                'label' => 'Description ou observation',
                'required' => false,
                'attr' => [
                    'class' => 'form-control',
                    'rows' => 4,
                    'placeholder' => 'Informations complémentaires...',
                ],
            ]);
    }

    public function configureOptions(
        OptionsResolver $resolver
    ): void {
        $resolver->setDefaults([
            'data_class' => CompteTresorerie::class,
            'attr' => [
                'novalidate' => 'novalidate',
            ],
        ]);
    }
}