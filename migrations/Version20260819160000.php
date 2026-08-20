<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260819160000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return "Corrige le defaut de articles.vendable (etait false, jamais coche par le formulaire de creation d'un article) : passe a true, et met a jour les articles existants pour qu'ils apparaissent dans la liste de selection d'une commande/d'un devis.";
    }

    public function up(Schema $schema): void
    {
        $this->addSql('ALTER TABLE articles ALTER vendable SET DEFAULT 1');
        $this->addSql('UPDATE articles SET vendable = 1 WHERE vendable = 0');
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE articles ALTER vendable SET DEFAULT 0');
    }
}
