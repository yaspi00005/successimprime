<?php

namespace App\Form;

use App\Entity\Paiements;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Symfony\Component\Form\Extension\Core\Type\IntegerType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class PaiementsType extends AbstractType
{
    public function buildForm(
        FormBuilderInterface $builder,
        array $options
    ): void {
        $builder
            ->add('montant', IntegerType::class, [
                'label' => 'Montant encaissé',
                'attr' => [
                    'class' => 'form-control',
                    'min' => 1,
                    'placeholder' => 'Exemple : 25 000',
                    'autocomplete' => 'off',
                ],
            ])

            ->add('mode', ChoiceType::class, [
                'label' => 'Mode de paiement',
                'choices' => [
                    'Espèces' => 'Espèces',
                    'Orange Money' => 'Orange Money',
                    'Moov Money' => 'Moov Money',
                    'Virement bancaire' => 'Virement bancaire',
                    'Chèque' => 'Chèque',
                    'Carte bancaire' => 'Carte bancaire',
                    'Autre' => 'Autre',
                ],
                'placeholder' => 'Sélectionner un mode',
                'attr' => [
                    'class' => 'form-control custom-select',
                ],
            ])

            ->add('reference', TextType::class, [
                'label' => 'Référence de paiement',
                'required' => false,
                'attr' => [
                    'class' => 'form-control',
                    'placeholder' => 'Numéro de transaction, chèque…',
                    'maxlength' => 255,
                    'autocomplete' => 'off',
                ],
                'help' => 'Facultative pour les paiements en espèces.',
            ]);
    }

    public function configureOptions(
        OptionsResolver $resolver
    ): void {
        $resolver->setDefaults([
            'data_class' => Paiements::class,
        ]);
    }
}