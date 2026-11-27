"""Informations locales vérifiées à la source, ajoutées le 19/11/2026.

- EXPE : les 23 territoires de l'expérimentation du financement des EHPAD (fusion des sections soins et
  dépendance, article 79 de la LFSS 2024, décret n° 2025-168 du 20/02/2025). Liste officielle :
  https://www.pour-les-personnes-agees.gouv.fr/actualites/financement-des-ehpad-une-experimentation-dans-23-departements
  (mise à jour du 03/02/2026). Pour le Rhône, seule la Métropole de Lyon participe.
- LOCAL : le service qui gère l'APA, relevé sur la fiche du département dans l'annuaire officiel
  pour-les-personnes-agees.gouv.fr/annuaire-departements/<département> et sur le site du département.
"""

MAJ_LOCAL = "2026-11-19"
PARTICIPATION_2026 = 6.16  # € par jour, participation forfaitaire des résidents en 2026 (6,10 € en 2025)

EXPE = {"11", "15", "17", "19", "22", "23", "29", "31", "40", "46", "47", "49", "52", "53", "56", "58", "62", "66", "73", "93", "973", "974"}
EXPE_METRO = "69"  # Métropole de Lyon seulement

SRC_EXPE = ('Source : <a href="https://www.pour-les-personnes-agees.gouv.fr/actualites/financement-des-ehpad-une-experimentation-dans-23-departements" '
            'rel="noopener" target="_blank">pour-les-personnes-agees.gouv.fr, « Financement des EHPAD : une expérimentation dans 23 départements »</a> '
            '(mise à jour du 03/02/2026), décret n° 2025-168 du 20 février 2025.')


def _a(url, txt):
    return f'<a href="{url}" rel="noopener" target="_blank">{txt}</a>'


ANN = "https://www.pour-les-personnes-agees.gouv.fr/annuaire-departements/"

# code -> dict(nom_aide, service, adresse, tel, courriel, liens [(texte, url)], texte (HTML), fiche, faq (q, r))
LOCAL = {
    "11": dict(service="Direction de l'autonomie du Département de l'Aude", adresse="Hôtel du département, allée Raymond-Courrière, 11855 Carcassonne Cedex 9", tel="04 68 11 68 11",
               liens=[("La page APA du Département", "https://www.aude.fr/quest-ce-que-lapa-et-comment-la-demander"), ("Les espaces seniors de l'Aude", "https://www.aude.fr/espaces-seniors")],
               texte="Dans l'Aude, l'accueil de proximité des personnes âgées passe par les espaces seniors, listés sur le site du Département. Ils peuvent aider à remplir le dossier avant l'envoi à Carcassonne.",
               fiche="aude-11"),
    "15": dict(service="Direction de l'autonomie du Département du Cantal", adresse="28 avenue Gambetta, 15015 Aurillac Cedex",
               liens=[("Les aides autonomie du Cantal", "https://www.cantal.fr/services-et-proximite/services/autonomie/#aides"), ("Le guide « Bien vieillir dans le Cantal » (septembre 2025)", "https://www.cantal.fr/wp-content/uploads/2025/09/bien-vieillir-dans-le-cantal-guide-personnes-agees-web.pdf"), ("Le site des aidants du Cantal", "https://www.aidants15.fr/")],
               texte="Le Département du Cantal publie un guide « Bien vieillir dans le Cantal » (édition de septembre 2025) qui recense les services d'aide, les établissements et les aides. Pour une place en EHPAD, la demande se fait en ligne sur ViaTrajectoire.",
               fiche="cantal-15"),
    "17": dict(service="Direction de l'autonomie du Département de la Charente-Maritime", adresse="85 boulevard de la République, 17076 La Rochelle Cedex 9",
               liens=[("La fiche APA du Département", "https://la.charente-maritime.fr/fiches-aides/lallocation-personnalisee-dautonomie-apa"), ("Vous avez des questions ? (points d'information)", "https://la.charente-maritime.fr/personnes-agees/vous-avez-des-questions")],
               texte="Le Département de la Charente-Maritime instruit les demandes depuis La Rochelle. Son espace « personnes âgées » regroupe aussi l'accueil familial et des ateliers pour les plus de 60 ans.",
               fiche="charente-maritime-17"),
    "19": dict(service="Direction de l'autonomie du Département de la Corrèze", adresse="Hôtel du département Marbot, 9 rue René-et-Émile-Fage, 19005 Tulle Cedex",
               liens=[("Les aides aux personnes âgées vivant à domicile", "https://www.correze.fr/services-en-ligne/les-aides/aide-en-faveur-des-personnes-agees-vivant-domicile"), ("Trouver une instance de coordination de l'autonomie (ICA)", "https://www.correze.fr/services-en-ligne/les-services-pres-de-chez-vous/les-services-du-conseil-departemental/les-instances-de-coordination-de-lautonomie-ica")],
               texte="En Corrèze, le relais local s'appelle l'instance de coordination de l'autonomie (ICA). Le Département propose aussi un formulaire de question en ligne réservé aux seniors.",
               fiche="correze-19"),
    "22": dict(service="Direction de l'autonomie du Département des Côtes-d'Armor", adresse="9 place du Général-de-Gaulle, CS 42371, 22023 Saint-Brieuc Cedex 1", tel="02 96 62 62 22",
               liens=[("La page APA du Département", "https://cotesdarmor.fr/vos-services/l-apa"), ("Les cinq Maisons du Département", "https://cotesdarmor.fr/vos-services/les-cinq-maisons-du-departement")],
               texte="Dans les Côtes-d'Armor, les cinq Maisons du Département servent de points d'accueil de proximité pour les questions d'autonomie, en plus du siège de Saint-Brieuc.",
               fiche="cotes-d-armor-22"),
    "23": dict(service="Direction de l'autonomie du Département de la Creuse", adresse="Hôtel du département, 4 place Louis-Lacrocq, 23011 Guéret Cedex",
               liens=[("La page APA du Département", "https://www.creuse.fr/L-Allocation-Personnalisee-d-Autonomie-APA"), ("Allo Répit (ouest Creuse)", "https://www.creuse.fr/Allo-Repit-Ouest-Creuse")],
               texte="La Creuse propose un service Allo Répit pour les aidants de l'ouest du département, et un transport adapté et accompagné pour les personnes âgées.",
               fiche="creuse-23"),
    "29": dict(service="Direction de l'autonomie du Département du Finistère", adresse="Hôtel du département, 32 boulevard Dupleix, 29196 Quimper Cedex", tel="02 98 76 20 20",
               liens=[("La page APA du Département", "https://www.finistere.fr/aides-et-services/personnes-agees/lallocation-personnalisee-dautonomie/"), ("Information et orientation des personnes âgées", "https://www.finistere.fr/aides-et-services/personnes-agees/information-et-orientation/")],
               texte="Le Finistère détaille sur son site l'APA, l'accueil familial et la vie en établissement. Les points d'information du département orientent les familles avant le dépôt du dossier à Quimper.",
               fiche="finistere-29"),
    "31": dict(service="Direction de l'autonomie du Département de la Haute-Garonne", adresse="1 boulevard de la Marquette, 31090 Toulouse Cedex 9", tel="05 34 33 32 31",
               liens=[("La page APA du Département", "https://www.haute-garonne.fr/allocation-personnalisee-dautonomie-apa"), ("Chèque Solidarité 31", "https://www.haute-garonne.fr/cheque-solidarite-31-pour-les-personnes-agees"), ("Téléassistance 31", "https://www.haute-garonne.fr/teleassistance-31"), ("Transports gratuits pour les personnes âgées", "https://www.haute-garonne.fr/transports-gratuits-pour-les-personnes-agees")],
               texte="La Haute-Garonne ajoute à l'APA ses propres aides : le Chèque Solidarité 31, la Téléassistance 31, le transport gratuit pour les personnes âgées et des haltes-répit pour les aidants. Les conditions sont sur le site du Département.",
               fiche="haute-garonne-31"),
    "40": dict(service="Direction de l'autonomie du Département des Landes", adresse="Hôtel du département, 23 rue Victor-Hugo, 40025 Mont-de-Marsan Cedex", tel="0800 40 04 04",
               liens=[("La page APA à domicile du Département", "https://www.landes.fr/toutes-nos-aides/allocation-personnalisee-dautonomie-domicile-apa"), ("Vivre en établissement dans les Landes", "https://www.landes.fr/maccompagne/personne-agee/vivre-en-etablissement")],
               texte="Les Landes donnent un numéro gratuit, le 0800 40 04 04, pour les questions d'autonomie. Près de chez votre parent, ce sont les Maisons landaises de la solidarité qui accueillent et aident à monter le dossier.",
               fiche="landes-40"),
    "46": dict(service="Direction de l'autonomie du Département du Lot", adresse="Avenue de l'Europe, Regourd, 46000 Cahors Cedex 9", tel="05 65 53 40 00",
               liens=[("APA et aides du Lot", "http://www.lot.fr/apa-aides"), ("Les espaces personnes âgées du Lot", "http://www.lot.fr/espaces-personnes-agees")],
               texte="Dans le Lot, l'accueil de proximité se fait dans les espaces personnes âgées du Département, qui aident aussi pour la téléassistance.",
               fiche="lot-46"),
    "47": dict(service="Direction de l'autonomie du Département de Lot-et-Garonne", adresse="Centre administratif, 1633 avenue du Général-Leclerc, 47922 Agen Cedex 9", tel="05 53 69 40 00",
               liens=[("Le maintien à domicile et l'APA", "https://www.lotetgaronne.fr/nos-services/solidarite/personnes-agees/maintien-a-domicile"), ("Demande d'aides à l'autonomie en ligne", "https://demande-autonomie.gouv.fr/")],
               texte="Le Lot-et-Garonne accepte la demande d'aides à l'autonomie à domicile en ligne, sur demande-autonomie.gouv.fr, en plus du dossier papier.",
               fiche="lot-et-garonne-47"),
    "49": dict(service="Direction de l'autonomie du Département de Maine-et-Loire (Maison départementale de l'autonomie)", adresse="Hôtel du département, CS 94104, 49941 Angers Cedex 9", tel="02 41 81 49 49",
               liens=[("APA à domicile (site de la MDA)", "https://www.mda.maine-et-loire.fr/aides-aux-personnes-agees/allocation-personnalisee-dautonomie-a-domicile-apa/"), ("L'annuaire des CLIC de Maine-et-Loire", "http://www.mda.maine-et-loire.fr/no_cache/annuaires-et-guides/annuaire-des-clic/"), ("Le site des aidants", "http://www.aidants49.fr/")],
               texte="En Maine-et-Loire, l'APA est présentée sur le site de la Maison départementale de l'autonomie (MDA), avec un annuaire des CLIC pour trouver le plus proche.",
               fiche="maine-et-loire-49"),
    "52": dict(service="Direction de l'autonomie du Département de la Haute-Marne, service Prestations à l'autonomie", adresse="Hôtel du département, 1 rue du Commandant Hugueny, 52905 Chaumont Cedex 9", tel="03 25 32 88 88",
               liens=[("Les aides à l'autonomie (APA, aide ménagère, téléassistance)", "https://haute-marne.fr/seniors/aide-autonomie/#aides"), ("Le bus de l'autonomie", "https://haute-marne.fr/seniors/le-bus-de-lautonomie/"), ("Demande d'aides à l'autonomie en ligne", "https://demande-autonomie.gouv.fr/")],
               texte="La Haute-Marne fait circuler un bus de l'autonomie dans le département. Son formulaire d'APA en établissement le dit noir sur blanc : pour un EHPAD situé en Haute-Marne, il n'y a pas de dossier d'APA en établissement à déposer depuis le 1er juillet 2025.",
               fiche="haute-marne-52"),
    "53": dict(service="Maison départementale de l'autonomie de la Mayenne (Direction de l'autonomie)", adresse="Centre Jean Monnet, 12 quai de Bootz, 53000 Laval", tel="02 43 677 577",
               liens=[("L'APA à domicile en Mayenne", "https://www.lamayenne.fr/service/lapa-domicile"), ("La Maison départementale de l'autonomie", "https://lamayenne.fr/service/la-maison-departementale-de-lautonomie-mda"), ("Demande d'aides à l'autonomie en ligne", "https://demande-autonomie.gouv.fr/")],
               texte="En Mayenne, la Maison départementale de l'autonomie (MDA) à Laval est l'interlocuteur unique pour l'APA. La demande peut aussi se faire en ligne.",
               fiche="mayenne-53"),
    "56": dict(service="Direction de l'autonomie du Département du Morbihan", adresse="2 rue de Saint-Tropez, BP 400, 56009 Vannes Cedex", tel="02 97 54 80 00",
               liens=[("La page APA à domicile du Département", "https://www.morbihan.fr/aides-et-services/soutien-aux-personnes-agees/allocation-personnalisee-dautonomie-apa-a-domicile"), ("Demande d'APA en ligne (mesaides.morbihan.fr)", "https://mesaides.morbihan.fr/aides")],
               texte="Le Morbihan a son propre portail de demande en ligne, mesaides.morbihan.fr, pour déposer la demande d'APA sans envoyer de papier.",
               fiche="morbihan-56"),
    "58": dict(service="Direction de l'autonomie du Département de la Nièvre", adresse="Hôtel du département, rue de la Préfecture, 58039 Nevers Cedex", tel="03 86 60 67 00",
               liens=[("Bien vieillir en Nièvre (APA, téléalarme, hébergement)", "https://nievre.fr/au-quotidien/solidarites/autonomie/bien-vieillir-en-nievre/"), ("Demande d'aides à l'autonomie en ligne", "https://demande-autonomie.gouv.fr/")],
               texte="La Nièvre réunit sur une seule page l'APA, la téléalarme et l'accueil en établissement. La demande d'aide à domicile peut se faire en ligne.",
               fiche="nievre-58"),
    "62": dict(service="Direction de l'autonomie du Département du Pas-de-Calais", adresse="Rue Ferdinand-Buisson, 62018 Arras Cedex 9",
               liens=[("La page APA du Département", "https://www.pasdecalais.fr/lallocation-personnalisee-dautonomie-apa"), ("À qui s'adresser dans le Pas-de-Calais", "https://www.pasdecalais.fr/qui-sadresser")],
               texte="Le Pas-de-Calais oriente les familles vers ses points d'accueil locaux depuis sa page « À qui s'adresser ». Pour une place en EHPAD, la demande se fait sur ViaTrajectoire.",
               fiche="pas-de-calais-62"),
    "66": dict(service="Direction de l'autonomie, service des prestations APA-PCH et CMI", adresse="30 rue Pierre-Bretonneau, 66000 Perpignan", tel="04 68 85 86 71", courriel="uipa@cd66.fr",
               liens=[("Vivre chez soi : formulaire APA et documents", "https://www.ledepartement66.fr/dossier/vivre-chez-soi/"), ("Les CLIC, vos interlocuteurs", "https://www.ledepartement66.fr/dossier/les-clics-vos-interlocuteurs-privilegies-2/")],
               texte="Dans les Pyrénées-Orientales, le service des prestations APA-PCH et CMI a son propre numéro, le 04 68 85 86 71, distinct du standard. Depuis le 1er octobre 2023, le même formulaire sert à demander l'APA au Département, l'aide « Bien vieillir chez soi » à la Carsat et l'aide à domicile de la MSA : en cas d'erreur, le dossier est réorienté vers le bon organisme. Le Département publie aussi la liste des services d'aide à domicile autorisés (mise à jour de septembre 2026).",
               fiche="pyrenees-orientales-66", site_src="https://www.ledepartement66.fr/dossier/vivre-chez-soi/"),
    "73": dict(service="Pôle social départemental de la Savoie", adresse="Place François-Mitterrand, CS 71806, 73018 Chambéry Cedex", tel="04 79 96 73 73",
               liens=[("La page APA du Département", "https://www.savoie.fr/web/psw_44024/aide-personnalisee-a-l-autonomie-apa"), ("Entrée en établissement", "https://www.savoie.fr/web/psw_44036/entree-en-etablissement-pour-personnes-agees")],
               texte="En Savoie, l'APA relève du Pôle social départemental de Chambéry. Le Département publie la liste des services d'aide à domicile et des établissements.",
               fiche="savoie-73"),
    "93": dict(nom_aide="ADPA (allocation départementale personnalisée d'autonomie)", service="Direction de l'autonomie du Département de la Seine-Saint-Denis",
               adresse="Hôtel du département, esplanade Jean-Moulin, 93006 Bobigny Cedex", tel="01 43 93 86 86", courriel="apa-domicile@seinesaintdenis.fr",
               liens=[("La Maison de l'autonomie et des aidant·es (MDAA)", "https://seinesaintdenis.fr/mdaa/"), ("Le compte Seine-Saint-Denis Autonomie", "https://seinesaintdenis.fr/mdaa/le-compte-seine-saint-denis-autonomie/"), ("L'espace seniors du Département", "https://seinesaintdenis.fr/solidarite/seniors/")],
               texte="En Seine-Saint-Denis, l'APA s'appelle l'<b>ADPA</b>, allocation départementale personnalisée d'autonomie : c'est la même aide, avec le même barème national. Le Département a ouvert la <b>Maison de l'autonomie et des aidant·es (MDAA)</b>, qui réunit l'accueil des personnes âgées, de la MDPH et des aidants. La Direction de l'autonomie répond au 01 43 93 86 86 (le standard du Département est le 01 43 93 93 93). Si votre parent emploie son aide à domicile en direct ou passe par un service mandataire, l'aide est versée sur le compte Seine-Saint-Denis Autonomie, à activer auprès de apa-domicile@seinesaintdenis.fr.",
               fiche="seine-saint-denis-93", site_src="https://seinesaintdenis.fr/mdaa/le-compte-seine-saint-denis-autonomie/",
               faq=[("Qu'est-ce que l'ADPA en Seine-Saint-Denis ?", "L'ADPA, allocation départementale personnalisée d'autonomie, est le nom donné à l'APA par le Département de la Seine-Saint-Denis. Les conditions et le barème sont les mêmes que l'APA partout en France. La Direction de l'autonomie répond au 01 43 93 86 86.")]),
    "973": dict(service="Direction de l'autonomie de la Collectivité territoriale de Guyane", adresse="Place Léopold-Héder, BP 5021, 97305 Cayenne Cedex", tel="05 94 31 20 31",
                liens=[("La Direction de l'autonomie de la CTG", "https://www.ctguyane.fr/pole-prevention-solidarite-sante-ppss/direction-de-lautonomie/")],
                texte="En Guyane, c'est la Collectivité territoriale (CTG) qui gère l'APA, par sa Direction de l'autonomie à Cayenne.",
                fiche="guyane-973"),
    "974": dict(service="Direction de l'autonomie du Département de La Réunion", adresse="2 rue de la Source, 97488 Saint-Denis Cedex", tel="02 62 90 30 30",
                liens=[("L'APA à domicile et en établissement", "https://www.departement974.fr/aide/aide-lallocation-personnalisee-dautonomie-domicile-en-etablissements-lapa"), ("Répit et repos pour les aidants", "https://www.departement974.fr/actualite/repit-repos")],
                texte="À La Réunion, le Département présente l'APA, l'aide ménagère, l'accueil familial et l'accueil de jour Alzheimer sur son site.",
                fiche="la-reunion-974"),
    "69": dict(nom_aide="ADPA dans le Rhône hors Métropole (allocation départementale personnalisée d'autonomie)", service="Direction de l'autonomie du Département du Rhône (hors Métropole de Lyon)",
               adresse="Hôtel du département, 29-31 cours de la Liberté, 69483 Lyon Cedex 03", tel="0800 86 98 69",
               liens=[("Fiche officielle du Département du Rhône", ANN + "rhone-69d"), ("Fiche officielle de la Métropole de Lyon", ANN + "metropole-de-lyon-69m")],
               texte="Le Département du Rhône appelle l'APA l'<b>ADPA</b> et répond au 0800 86 98 69, numéro gratuit, pour les communes hors Métropole. Pour Lyon, Villeurbanne et les autres communes de la Métropole, c'est la Direction de l'autonomie de la Métropole de Lyon (20 rue du Lac, 69505 Lyon Cedex 03, 04 78 63 40 40).",
               fiche="rhone-69d"),
    # Pages à dédoublonner en priorité (audit du 19/11) : informations propres au département
    "18": dict(service="Direction Autonomie Personnes âgées Personnes handicapées du Cher", adresse="Pyramides du Conseil départemental, 7 route de Guerry, 18000 Bourges",
               liens=[("Maintien à domicile : APA et aide ménagère", "https://www.departement18.fr/Maintien-a-domicile"), ("Vie en établissement", "https://www.departement18.fr/Vie-en-etablissement")],
               texte="Dans le Cher, la Direction Autonomie partage le site des Pyramides, route de Guerry à Bourges, avec la MDPH. Le Département met en ligne un dossier commun « APA et caisses de retraite » : un seul formulaire suffit, il est orienté vers le bon organisme. L'APA y finance l'aide à domicile, l'accueil de jour, la téléalarme, le portage de repas et les frais de change. Pour l'aide ménagère (65 ans et plus, GIR 5 ou 6, faibles ressources), le dossier se dépose au CCAS de la mairie, pas au Département.",
               fiche="cher-18", site_src="https://www.departement18.fr/Maintien-a-domicile"),
    "27": dict(service="Direction de l'autonomie du Département de l'Eure", adresse="14 boulevard Georges-Chauvin, 27021 Évreux Cedex", tel="02 32 31 50 50",
               liens=[("Tout savoir sur l'APA dans l'Eure", "https://eureennormandie.fr/ca-peut-nous-arriver/bien-vieillir-et-soutenir-lautonomie/allocation-personnalisee-dautonomie-apa-1/"), ("L'aide sociale à l'hébergement", "https://eureennormandie.fr/nos-aides-et-services/particuliers/seniors-aidants/les-aides-financieres/lash-une-aide-a-lhebergement/"), ("Le livret individuel d'accompagnement", "https://eureennormandie.fr/nos-aides-et-services/particuliers/seniors-aidants/reflechir-a-son-parcours-residentiel/le-livret-individuel-daccompagnement-le-document-indispensable-a-avoir-chez-soi/")],
               texte="Le Département de l'Eure a deux dossiers distincts : l'un pour l'APA à domicile (le formulaire national), l'autre pour l'APA en établissement. Les formulaires se retirent en mairie, au CCAS ou dans une Maison France Services. Le Département propose aussi un livret individuel d'accompagnement, à garder chez la personne âgée pour réunir ses informations utiles.",
               fiche="eure-27", site_src="https://eureennormandie.fr/ca-peut-nous-arriver/bien-vieillir-et-soutenir-lautonomie/allocation-personnalisee-dautonomie-apa-1/"),
    "70": dict(service="Direction de l'autonomie du Département de la Haute-Saône", adresse="Hôtel du département, 23 rue de la Préfecture, 70006 Vesoul Cedex", tel="03 84 95 70 70",
               liens=[("Les missions solidarités du Département", "https://www.haute-saone.fr/le-departement/les-competences/solidarites/")],
               texte="En Haute-Saône, la Direction de l'autonomie à Vesoul attribue et verse l'APA, à domicile comme en établissement. Le Département finance aussi l'aide-ménagère et l'hébergement en EHPAD des personnes âgées aux revenus modestes, au titre de l'aide sociale, et soutient une plateforme de répit départementale pour les aidants.",
               fiche="haute-saone-70", site_src="https://www.haute-saone.fr/le-departement/les-competences/solidarites/"),
}


# 27/11/2026 : les 75 départements qui n'avaient pas de bloc local, relevés sur les sites officiels (Département, annuaire
# pour-les-personnes-agees.gouv.fr), chaque fait avec son URL dans _data/local-apa-2026-11-27.json (champ « faits », non affiché).
import json as _json, os as _os
_P = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "_data", "local-apa-2026-11-27.json")
for _k, _v in _json.load(open(_P, encoding="utf-8")).items():
    LOCAL.setdefault(_k, _v)
