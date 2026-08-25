<?php

namespace App\Repository;

use App\Entity\Notification;
use App\Entity\User;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<Notification>
 */
class NotificationRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, Notification::class);
    }

    /**
     * @return Notification[]
     */
    public function findNonLuesPourUtilisateur(User $utilisateur, int $limite = 10): array
    {
        return $this->createQueryBuilder('n')
            ->andWhere('n.destinataire = :destinataire')
            ->andWhere('n.lue = false')
            ->setParameter('destinataire', $utilisateur)
            ->orderBy('n.dateCreation', 'DESC')
            ->setMaxResults($limite)
            ->getQuery()
            ->getResult();
    }
}
