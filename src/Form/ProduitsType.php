<?php

namespace App\Form;

use App\Entity\CategorieProduit;
use App\Entity\Finition;
use App\Entity\Format;
use App\Entity\Produits;
use App\Entity\Supports;
use App\Entity\TypesImpression;
use Symfony\Bridge\Doctrine\Form\Type\EntityType;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class ProduitsType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder
            ->add('nom')
            ->add('description')
            ->add('publie')
            ->add('ordre')
            ->add('code')
            ->add('prixBase')
            ->add('personnalisable')
            ->add('actif')
            ->add('categorieProduit', EntityType::class, [
                'class' => CategorieProduit::class,
                'choice_label' => 'id',
            ])
            ->add('typesImpressions', EntityType::class, [
                'class' => TypesImpression::class,
                'choice_label' => 'id',
                'multiple' => true,
            ])
            ->add('supports', EntityType::class, [
                'class' => Supports::class,
                'choice_label' => 'id',
                'multiple' => true,
            ])
            ->add('formats', EntityType::class, [
                'class' => Format::class,
                'choice_label' => 'id',
                'multiple' => true,
            ])
            ->add('finitions', EntityType::class, [
                'class' => Finition::class,
                'choice_label' => 'id',
                'multiple' => true,
            ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        $resolver->setDefaults([
            'data_class' => Produits::class,
        ]);
    }
}
