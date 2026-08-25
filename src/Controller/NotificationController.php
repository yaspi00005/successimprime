<?php

namespace App\Controller;

use App\Entity\Notification;
use App\Entity\User;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/notifications', name: 'app_notification_')]
final class NotificationController extends AbstractController
{
    /**
     * Marque la notification comme lue puis redirige vers sa cible
     * (ou vers l'accueil si elle n'a pas de route associée).
     */
    #[Route('/{id}/ouvrir', name: 'ouvrir', requirements: ['id' => '\d+'], methods: ['GET'])]
    public function ouvrir(Notification $notification, EntityManagerInterface $entityManager): Response
    {
        $utilisateur = $this->getUser();

        if (!$utilisateur instanceof User || $notification->getDestinataire() !== $utilisateur) {
            throw $this->createAccessDeniedException('Cette notification ne vous appartient pas.');
        }

        if (!$notification->isLue()) {
            $notification->marquerLue();
            $entityManager->flush();
        }

        if ($notification->getRoute() !== null) {
            return $this->redirectToRoute($notification->getRoute(), $notification->getRouteParametres());
        }

        return $this->redirectToRoute('app_home');
    }
}
