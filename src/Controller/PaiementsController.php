<?php

namespace App\Controller;

use App\Entity\Paiements;
use App\Form\PaiementsType;
use App\Repository\PaiementsRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/paiements')]
final class PaiementsController extends AbstractController
{
    #[Route(name: 'app_paiements_index', methods: ['GET'])]
    public function index(PaiementsRepository $paiementsRepository): Response
    {
        return $this->render('paiements/index.html.twig', [
            'paiements' => $paiementsRepository->findAll(),
        ]);
    }

    #[Route('/new', name: 'app_paiements_new', methods: ['GET', 'POST'])]
    public function new(Request $request, EntityManagerInterface $entityManager): Response
    {
        $paiement = new Paiements();
        $form = $this->createForm(PaiementsType::class, $paiement);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $entityManager->persist($paiement);
            $entityManager->flush();

            return $this->redirectToRoute('app_paiements_index', [], Response::HTTP_SEE_OTHER);
        }

        return $this->render('paiements/new.html.twig', [
            'paiement' => $paiement,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_paiements_show', methods: ['GET'])]
    public function show(Paiements $paiement): Response
    {
        return $this->render('paiements/show.html.twig', [
            'paiement' => $paiement,
        ]);
    }

    #[Route('/{id}/edit', name: 'app_paiements_edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, Paiements $paiement, EntityManagerInterface $entityManager): Response
    {
        $form = $this->createForm(PaiementsType::class, $paiement);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $entityManager->flush();

            return $this->redirectToRoute('app_paiements_index', [], Response::HTTP_SEE_OTHER);
        }

        return $this->render('paiements/edit.html.twig', [
            'paiement' => $paiement,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_paiements_delete', methods: ['POST'])]
    public function delete(Request $request, Paiements $paiement, EntityManagerInterface $entityManager): Response
    {
        if ($this->isCsrfTokenValid('delete'.$paiement->getId(), $request->getPayload()->getString('_token'))) {
            $entityManager->remove($paiement);
            $entityManager->flush();
        }

        return $this->redirectToRoute('app_paiements_index', [], Response::HTTP_SEE_OTHER);
    }
}
