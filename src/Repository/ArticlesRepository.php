<?php

namespace App\Repository;

use App\Entity\Articles;
use App\Entity\StockEntrees;
use App\Entity\StockSorties;

use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<Articles>
 */
class ArticlesRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Articles::class);
    }
    public function calculerStockDisponible(
    Articles $article,
    EntityManagerInterface $em
): int {
    $totalEntrees = (int) $em
        ->getRepository(StockEntrees::class)
        ->createQueryBuilder('e')
        ->select('COALESCE(SUM(e.quantites), 0)')
        ->andWhere('e.article = :article')
        ->setParameter('article', $article)
        ->getQuery()
        ->getSingleScalarResult();

    $totalSorties = (int) $em
        ->getRepository(StockSorties::class)
        ->createQueryBuilder('s')
        ->select('COALESCE(SUM(s.quantite), 0)')
        ->andWhere('s.article = :article')
        ->setParameter('article', $article)
        ->getQuery()
        ->getSingleScalarResult();

    return $totalEntrees - $totalSorties;
}

    /**
     * Articles utilisables comme consommables de production
     * (colle, encre, film...) : jamais vendus directement au
     * client, donc exclus de "Article en stock" côté commande
     * (vendable = false).
     *
     * @return Articles[]
     */
    public function findConsommables(): array
    {
        return $this->createQueryBuilder('a')
            ->andWhere('a.vendable = :vendable')
            ->andWhere('a.actif = :actif')
            ->setParameter('vendable', false)
            ->setParameter('actif', true)
            ->orderBy('a.designation', 'ASC')
            ->getQuery()
            ->getResult();
    }

    //    /**
    //     * @return Articles[] Returns an array of Articles objects
    //     */
    //    public function findByExampleField($value): array
    //    {
    //        return $this->createQueryBuilder('a')
    //            ->andWhere('a.exampleField = :val')
    //            ->setParameter('val', $value)
    //            ->orderBy('a.id', 'ASC')
    //            ->setMaxResults(10)
    //            ->getQuery()
    //            ->getResult()
    //        ;
    //    }

    //    public function findOneBySomeField($value): ?Articles
    //    {
    //        return $this->createQueryBuilder('a')
    //            ->andWhere('a.exampleField = :val')
    //            ->setParameter('val', $value)
    //            ->getQuery()
    //            ->getOneOrNullResult()
    //        ;
    //    }
}
