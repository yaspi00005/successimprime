<?php

namespace App\Form;

use App\Entity\Format;
use App\Entity\ProduitConfiguration;
use App\Entity\Produits;
use App\Entity\Supports;
use App\Entity\TypesImpression;
use Symfony\Bridge\Doctrine\Form\Type\EntityType;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class ProduitConfigurationType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('active')
            ->add('ordre')
            ->add('description')
            ->add('prixBase')
            ->add('modeCalcul')
            ->add('quantiteMinimale')
            ->add('quantiteMaximale')
            ->add('produit', EntityType::class, [
                'class' => Produits::class,
                'choice_label' => 'id',
            ])
            ->add('typeImpression', EntityType::class, [
                'class' => TypesImpression::class,
                'choice_label' => 'id',
            ])
            ->add('support', EntityType::class, [
                'class' => Supports::class,
                'choice_label' => 'id',
            ])
            ->add('format', EntityType::class, [
                'class' => Format::class,
                'choice_label' => 'id',
            ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => ProduitConfiguration::class,
        ]);
    }
}
