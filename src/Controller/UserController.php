<?php

namespace App\Controller;

use App\Entity\User;
use App\Form\UserType;
use App\Repository\UserRepository;
use App\Repository\EmployesRepository;
use Doctrine\ORM\EntityManagerInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/user')]
final class UserController extends AbstractController
{
    #[Route(name: 'app_user_index', methods: ['GET'])]
    public function index(UserRepository $userRepository): Response
    {

        return $this->render('user/index.html.twig', [
            'users' => $userRepository->findAll(),
        ]);
    }

    #[Route('/new', name: 'app_user_new', methods: ['GET', 'POST'])]
    public function new(Request $request, EntityManagerInterface $entityManager): Response
    {
        $user = new User();
        $form = $this->createForm(UserType::class, $user);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $entityManager->persist($user);
            $entityManager->flush();

            return $this->redirectToRoute('app_user_index', [], Response::HTTP_SEE_OTHER);
        }

        return $this->render('user/new.html.twig', [
            'user' => $user,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_user_show', methods: ['GET'])]
    public function show(User $user): Response
    {
        return $this->render('user/show.html.twig', [
            'user' => $user,
        ]);
    }

    #[Route('/{id}/edit', name: 'app_user_edit', methods: ['GET', 'POST'])]
    public function edit(Request $request, User $user, EntityManagerInterface $entityManager): Response
    {
        $form = $this->createForm(UserType::class, $user);
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $entityManager->flush();

            return $this->redirectToRoute('app_user_index', [], Response::HTTP_SEE_OTHER);
        }

        return $this->render('user/edit.html.twig', [
            'user' => $user,
            'form' => $form,
        ]);
    }

    #[Route('/{id}', name: 'app_user_delete', methods: ['POST'])]
    public function delete(Request $request, User $user, EntityManagerInterface $entityManager): Response
    {
        if ($this->isCsrfTokenValid('delete' . $user->getId(), $request->getPayload()->getString('_token'))) {
            $entityManager->remove($user);
            $entityManager->flush();
        }

        return $this->redirectToRoute('app_user_index', [], Response::HTTP_SEE_OTHER);
    }

    #[Route(
        '/create/ajax',
        name: 'user_create_ajax',
        methods: ['POST']
    )]
    public function createAjax(
        Request $request,
        EntityManagerInterface $entityManager,
        UserRepository $userRepository,
        EmployesRepository $employesRepository
    ): JsonResponse {


        // Vérification CSRF

        if (!$this->isCsrfTokenValid(
            'create_user',
            $request->request->get('_token')
        )) {


            return new JsonResponse([

                'success' => false,

                'message' => 'Token de sécurité invalide'

            ], 403);
        }



        $username = $request->request->get('username');


        $roles = $request->request->all('roles');

        $employeId = $request->request->get('employeId');


        $employe = $employesRepository->find($employeId);


        $actif = $request->request->get('actif') ? true : false;



        // Vérification username

        if ($userRepository->findOneBy([
            'username' => $username
        ])) {


            return new JsonResponse([

                'success' => false,

                'message' => 'Ce username existe déjà'

            ]);
        }

        if (!$employe) {


            return new JsonResponse([

                'success' => false,

                'message' => 'Employé introuvable'

            ]);
        }




        // Sécurité rôles autorisés

        $rolesAutorises = [

            'ROLE_ADMIN',
            'ROLE_MACHINISTE_DTF',
            'ROLE_MACHINISTE_TRACER',
            'ROLE_REPROGRAPHIE',
            'ROLE_GRAPHISME',
            'ROLE_CAISSE',
            'ROLE_STOCK',
            'ROLE_COMPTABILITE',
            'ROLE_LOGISTIQUE'

        ];



        $roles = array_intersect(
            $roles,
            $rolesAutorises
        );

        if ($employe->getUser()) {

            return new JsonResponse([
                'success' => false,
                'message' => 'Cet employé possède déjà un compte'
            ]);
        }

        $roles_controle = $roles ?? [];


        if (empty($roles_controle)) {

            return $this->json([
                'success' => false,
                'message' => 'Veuillez attribuer au moins un rôle.Merci de contacter l\'administrateur si le problème persiste.'
            ], 400);
        }

        $user = new User();


        $user->setUsername($username);



        // Enregistrement JSON

        $user->setRoles($roles);



        $user->setActif($actif);


        $user->setEmploye($employe);
        $user->setDateAdd(new \DateTime());
        $user->setDateUpdate(new \DateTime());



        // mot de passe initial

        $user->setPassword(
            password_hash(
                '123456',
                PASSWORD_DEFAULT
            )
        );



        $entityManager->persist($user);


        $entityManager->flush();



        return new JsonResponse([


            'success' => true,

            'message' => 'Compte utilisateur créé avec succès'


        ]);
    }

    #[Route(
        '/user/{id}/roles/update',
        name: 'app_user_roles_update',
        methods: ['POST']
    )]
    #[IsGranted('ROLE_ADMIN')]
    public function updateUserRoles(
        User $user,
        Request $request,
        EntityManagerInterface $entityManager
    ): JsonResponse {
        $data = json_decode($request->getContent(), true);

        if (!is_array($data)) {
            return $this->json([
                'success' => false,
                'message' => 'Les données JSON sont invalides.',
            ], 400);
        }

        $roles = $data['roles'] ?? [];
        $actif = (bool) ($data['actif'] ?? false);

        if (!is_array($roles) || count($roles) === 0) {
            return $this->json([
                'success' => false,
                'message' => 'Veuillez sélectionner au moins un rôle.',
            ], 400);
        }

        $rolesAutorises = [
            'ROLE_ADMIN',
            'ROLE_MACHINISTE_DTF',
            'ROLE_MACHINISTE_TRACER',
            'ROLE_REPROGRAPHIE',
            'ROLE_GRAPHISME',
            'ROLE_CAISSE',
            'ROLE_STOCK',
            'ROLE_COMPTABILITE',
            'ROLE_LOGISTIQUE',
        ];

        $rolesValides = array_values(array_unique(array_intersect(
            $roles,
            $rolesAutorises
        )));

        if (count($rolesValides) === 0) {
            return $this->json([
                'success' => false,
                'message' => 'Aucun rôle valide n’a été sélectionné.',
            ], 400);
        }

        /*
     * getRoles() ajoute déjà ROLE_USER automatiquement.
     * Il n'est donc pas obligatoire de l'enregistrer dans la colonne JSON.
     */
        $user->setRoles($rolesValides);
        $user->setActif($actif);
        $user->setDateUpdate(new \DateTime());

        $entityManager->flush();

        return $this->json([
            'success' => true,
            'message' => 'Les rôles ont été mis à jour avec succès.',
            'user' => [
                'id' => $user->getId(),
                'roles' => $user->getRoles(),
                'actif' => $user->isActif(),
            ],
        ]);
    }

    #[Route(
        '/user/{id}/delete/ajax',
        name: 'app_user_delete_ajax',
        methods: ['DELETE']
    )]
    #[IsGranted('ROLE_ADMIN')]
    public function deleteUserAjax(
        User $user,
        Request $request,
        EntityManagerInterface $entityManager
    ): JsonResponse {
        $data = json_decode($request->getContent(), true);

        $token = $data['_token'] ?? null;

        if (!$this->isCsrfTokenValid('delete_user_' . $user->getId(), $token)) {
            return $this->json([
                'success' => false,
                'message' => 'Jeton de sécurité invalide.',
            ], 403);
        }

        if ($this->getUser() === $user) {
            return $this->json([
                'success' => false,
                'message' => 'Vous ne pouvez pas supprimer votre propre compte.',
            ], 403);
        }

        $entityManager->remove($user);
        $entityManager->flush();

        return $this->json([
            'success' => true,
            'message' => 'Le compte utilisateur a été supprimé.',
        ]);
    }
    #[Route(
        '/user/{id}/roles',
        name: 'app_user_roles_get',
        methods: ['GET']
    )]
    #[IsGranted('ROLE_ADMIN')]
    public function getUserRoles(User $user): JsonResponse
    {
        return $this->json([
            'success' => true,
            'user' => [
                'id' => $user->getId(),
                'username' => $user->getUsername(),
                'roles' => $user->getRoles(),
                'actif' => $user->isActif(),
            ],
        ]);
    }
    #[Route(
        '/user/{id}/toggle-status',
        name: 'app_user_toggle_status',
        methods: ['POST']
    )]
    #[IsGranted('ROLE_ADMIN')]
    public function toggleStatus(
        User $user,
        Request $request,
        EntityManagerInterface $entityManager
    ): JsonResponse {
        $data = json_decode($request->getContent(), true);

        if (!is_array($data)) {
            return $this->json([
                'success' => false,
                'message' => 'Données invalides.',
            ], 400);
        }

        $token = $data['_token'] ?? null;

        if (!$this->isCsrfTokenValid(
            'toggle_user_' . $user->getId(),
            $token
        )) {
            return $this->json([
                'success' => false,
                'message' => 'Jeton de sécurité invalide.',
            ], 403);
        }

        if ($this->getUser() === $user && $user->isActif()) {
            return $this->json([
                'success' => false,
                'message' => 'Vous ne pouvez pas désactiver votre propre compte.',
            ], 403);
        }

        $nouvelEtat = !$user->isActif();

        $user->setActif($nouvelEtat);
        $user->setDateUpdate(new \DateTime());

        $entityManager->flush();

        return $this->json([
            'success' => true,
            'message' => $nouvelEtat
                ? 'Le compte a été activé avec succès.'
                : 'Le compte a été désactivé avec succès.',
            'actif' => $nouvelEtat,
        ]);
    }
}
