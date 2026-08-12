<?php

namespace App\Service;

use Symfony\Contracts\HttpClient\HttpClientInterface;

final class WhatsAppService
{
    public function __construct(
        private readonly HttpClientInterface $httpClient,
        private readonly string $accessToken,
        private readonly string $phoneNumberId,
        private readonly string $apiVersion
    ) {
    }

    public function envoyerTemplate(
        string $telephone,
        string $template,
        string $langue = 'fr',
        array $parametres = []
    ): array {
        $telephone = $this->normaliserTelephone(
            $telephone
        );

        $components = [];

        if ($parametres !== []) {
            $parameters = [];

            foreach ($parametres as $parametre) {
                $parameters[] = [
                    'type' => 'text',
                    'text' => (string) $parametre,
                ];
            }

            $components[] = [
                'type' => 'body',
                'parameters' => $parameters,
            ];
        }

        $response = $this->httpClient->request(
            'POST',
            sprintf(
                'https://graph.facebook.com/%s/%s/messages',
                $this->apiVersion,
                $this->phoneNumberId
            ),
            [
                'headers' => [
                    'Authorization' =>
                        'Bearer ' . $this->accessToken,

                    'Content-Type' =>
                        'application/json',
                ],

                'json' => [
                    'messaging_product' =>
                        'whatsapp',

                    'recipient_type' =>
                        'individual',

                    'to' =>
                        $telephone,

                    'type' =>
                        'template',

                    'template' => [
                        'name' =>
                            $template,

                        'language' => [
                            'code' =>
                                $langue,
                        ],

                        'components' =>
                            $components,
                    ],
                ],
            ]
        );

        return $response->toArray(false);
    }


    private function normaliserTelephone(
        string $telephone
    ): string {
        $telephone = preg_replace(
            '/\D+/',
            '',
            $telephone
        ) ?? '';

        /*
         * Mali :
         * 78478742
         * devient
         * 22378478742
         */
        if (
            strlen($telephone) === 8
        ) {
            $telephone =
                '223' . $telephone;
        }

        return $telephone;
    }
}