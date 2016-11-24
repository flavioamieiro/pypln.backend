# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.


import subprocess
import re
from pypln.backend.celery_task import PyPLNTask

SEMANTIC_TAGS = \
{
    'Animal':
        {
        '<A>': 'Animal, umbrella tag (clone, fêmea, fóssil, parasito, predador)' ,
        '<AA>': 'Group of animals (cardume, enxame, passarada, ninhada)',
        '<Adom>': 'Domestic animal or big mammal (likely to have female forms etc.: terneiro, leão/leoa, cachorro)',
        '<AAdom>': 'Group of domestic animals (boiada)',
        '<Aich>': 'Water-animal (tubarão, delfim)',
        '<Amyth>': 'Mythological animal (basilisco)',
        '<Azo>': 'Land-animal (raposa)',
        '<Aorn>': 'Bird (águia, bem-te-vi)',
        '<Aent>': 'Insect (borboleta)',
        '<Acell>': 'Cell-animal (bacteria, blood cells: linfócito)',
        },
    'Plant':
        {
        '<B>': 'Plant, umbrella tag',
        '<BB>': 'Group of plants, plantation (field, forest etc.: mata, nabal)',
        '<Btree>': 'Tree (oliveira, palmeira)',
        '<Bflo>': 'Flower (rosa, taraxaco)',
        '<Bbush>': 'Bush, shrub (rododendro, tamariz)',
        '<fruit>': '(fruit, berries, nuts: maçã, morango, avelã, melancia)',
        '<Bveg>': '(vegetable espargo, funcho)',
        },
    'Human':
        {
        '<H>': 'Human, umbrella tag',
        '<HH>': 'Group of humans (organisations, teams, companies, e.g. editora)',
        '<Hattr>': 'Attributive human umbrella tag (many -ista, -ante)',
        '<Hbio>': 'Human classified by biological criteria (race, age etc., caboclo, mestiço, bebé, adulto)',
        '<Hfam>': 'Human with family or other private relation (pai, noiva)',
        '<Hideo>': 'Ideological human (comunista, implies <Hattr>), also: follower, disciple (dadaista)',
        '<Hmyth>': 'Humanoid mythical (gods, fairy tale humanoids, curupira, duende)',
        '<Hnat>': 'Nationality human (brasileiro, alemão), also: inhabitant (lisboeta)',
        '<Hprof>': 'Professional human (marinheiro, implies <Hattr>), also: sport, hobby (alpinista)',
        '<Hsick>': 'Sick human (few: asmático, diabético, cp <sick>)',
        '<Htit>': 'Title noun (rei, senhora)',
        },
    'Place and spatial':
        {
        '<L>': 'Place, umbrella tag',
        '<Labs>': 'Abstract place (anverso. auge)',
        '<Lciv>': 'Civitas, town, country, county (equals <L> + <HH>, cidade, país)',
        '<Lcover>': 'Cover, lid (colcha, lona, tampa)',
        '<Lh>': 'Functional place, human built or human-used (aeroporto, anfiteatro, cp. <build> for just a building)',
        '<Lopening>': 'opening, hole (apertura, fossa)',
        '<Lpath>': 'Path (road, street etc.: rua, pista)' ,
        '<Lstar>': 'Star object (planets, comets: planeta, quasar)',
        '<Lsurf>': 'surface (face, verniz, cp. <Lcover>)',
        '<Ltip>': 'tip place, edge (pico, pontinha, cp. <Labs>)',
        '<Ltop>': 'Geographical, natural place (promontório, pântano)',
        '<Ltrap>': 'trap place (armadilha, armazelo)',
        '<Lwater>': 'Water place (river, lake, sea: fonte, foz, lagoa)',
        '<bar>': 'barrier noun (dique, limite, muralha)',
        '<build>': '(building)',
        '<inst>': '(institution)',
        '<pict>': '(picture)',
        '<sit>': '(situation)',
        '<pos-an>': 'anatomical/body position (few: desaprumo)',
        '<pos-soc>': 'social position, job (emprego, condado, capitania, presidência)',
        },
    'Vehicle':
        {
        '<V>': 'Vehicle, umbrella tag and ground vehicle (car, train: carro, comboio, tanque, teleférico)',
        '<VV>': 'Group of vehicles (armada, convoy: frota, esquadra)',
        '<Vwater>': 'Water vehicle (ship: navio, submersível, canoa)',
        '<Vair>': 'Air vehicle (plane: hidroplano, jatinho)',
        },
    'Abstract':
        {
        '<ac>': 'Abstract countable, umbrella tag (alternativa, chance, lazer)',
        '<ac-cat>': 'Category word (latinismo, número atômico)',
        '<ac-sign>': 'sign, symbol (parêntese, semicolcheia)',
        '<am>': 'Abstract mass/non-countable, umbrella tag (still contains many cases that could be <f-..>, e.g. habilidade, legalidade)',
        '<ax>': 'Abstract/concept, neither countable nor mass (endogamia), cp. <f>, <sit> etc.',
        '<f...>': '(features)',
        '<dir>': 'direction noun (estibordo, contrasenso, norte)',
        '<geom...>': '(shapes)',
        '<meta>': 'meta noun (tipo, espécie)',
        '<brand>': '(MARCA) brand',
        '<genre>': '(DISCIPLINA) subject matter',
        '<school>': '(ESCOLA) school of thought',
        '<idea>': '(IDEA) idea, concept',
        '<plan>': '(PLANO) named plan, project',
        '<author>': '(OBRA) artist-s name, standing for body of work',
        '<absname>': '(NOME)',
        '<disease>': '(ESTADO) physiological state, in particular: disease',
        },
    'Concept':
        {
        '<conv>': 'convention (social rule or law, lei, preceito)',
        '<domain>': 'subject matter, profession, cf. <genre>, anatomia, citricultura, dactilografia)',
        '<ism>': 'ideology or other value system (anarquismo, anti-ocidentalismo, apartheid)',
        '<genre>': '',
        '<ling>': 'language (alemão, catalão, bengali)',
        '<disease>': '',
        '<state...>': '',
        '<therapy>': 'therapy (also <domain> and <activity>, acupuntura, balneoterapia)',
        },
    'Game':
        {
        '<game>': 'play, game (bilhar, ioiô, poker, also <activity>)',
        },
    'Genre':
        {
        '<genre>': 'genre (especially art genre, cf. <domain>, modernismo, tropicalismo)',
        },
    'Quantity':
        {
        '<unit>': '',
        '<amount>': 'quantity noun (bocada, teor, sem-fim)',
        '<cur>': 'currency noun (countable, implies <unit>, cf. <mon>, dirham, euro, real, dólar)',
        '<mon>': 'amount of money (bolsa, custo, imposto, cf. <cur>)',
        },
    'Action':
        {
        '<act>': 'Action umbrella tag (+CONTROL, PERFECTIVE)',
        '<act-beat>': 'beat-action (thrashing, pancada, surra)',
        '<act-d>': 'do-action (typically dar/fazer + N, tentativa, teste, homenagem)',
        '<act-s>': 'speech act or communicative act (proposta, ordem)',
        '<act-trick>': 'trick-action (cheat, fraud, ruse, jeito, fraude, similar to <act-d>)',
        '<activity>': 'Activity, umbrella tag (+CONTROL, IMPERFECTIVE, correria, manejo)',
        '<sport>': '',
        '<game>': '',
        '<therapy>': '',
        '<dance>': 'dance (both <activity>, <genre> and <sem-l>, calipso, flamenco, forró)',
        '<fight>': 'fight, conflict (also <activity> and +TEMP, briga, querela)',
        '<talk>': 'speech situation, talk, discussion, quarrel (implies <activity> and <sd>, entrevista, lero-lero)',
        },
    'Anatomical':
        {
        '<an>': 'Anatomical noun, umbrella tag (carótida, clítoris, dorso)',
        '<anmov>': 'Movable anatomy (arm, leg, braço, bíceps, cotovelo)',
        '<anorg>': 'Organ (heart, liver, hipófise, coração, testículo)',
        '<anost>': 'Bone (calcâneo, fíbula, vértebra)',
        '<anzo>': 'Animal anatomy (rúmen, carapaça, chifres, tromba)',
        '<anorn>': 'Bird anatomy (bico, pluma)',
        '<anich>': 'Fish anatomy (few: bránquias, siba)',
        '<anent>': 'Insect anatomy (few: tentáculo, olho composto)',
        '<anbo>': 'Plant anatomy (bulbo, caule, folha)',
        '<f-an>': '(human anatomical feature)',
        },
    'Thing':
        {
        '<cc>': 'Concrete countable object, umbrella tag (briquete, coágulo, normally movable things, unlike <part-build>)',
        '<cc-h>': 'Artifact, umbrella tag (so far empty category in PALAVRAS)',
        '<cc-beauty>': 'ornamental object (few: guirlanda, rufo)',
        '<cc-board>': 'flat long object (few: board, plank, lousa, tabla)',
        '<cc-fire>': 'fire object (bonfire, spark, chispa, fogo, girândola)',
        '<cc-handle>': 'handle (garra, ansa, chupadouro)',
        '<cc-light>': 'light artifact (lampião, farol, projector) ',
        '<cc-particle>': '(atomic) particle (few: cátion, eletrônio)',
        '<cc-r>': 'read object (carteira, cupom, bilhete, carta, cf. <sem-r>)',
        '<cc-rag>': 'cloth object (towel, napkin, carpet, rag) , cp. <mat-cloth>',
        '<cc-stone>': '(cc-round) stones and stone-sized round objects (pedra, itá, amonite, tijolo)',
        '<cc-stick>': 'stick object (long and thin, vara, lançe, paulito)',
        '<object>': '(OBJECT) named object',
        '<common>': '(OBJECT) common noun used as name',
        '<mat>': '(SUBSTANCIA) substance',
        '<class>': '(CLASSE) classification category for things',
        '<plant>': '(CLASSE) plant name',
        '<currency>': '(MOEDA) currency name (also marked on the number)',
        '<mass>': 'mass noun (e.g. "leite", "a-gua")',
        '<furn>': 'furniture (cama, cadeira, tambo, quadro)',
        '<con>': 'container (implies <num+> quantifying, ampola, chícara, aquário)',
        },
    'Substance':
        {
        '<cm>': 'concrete mass/non-countable, umbrella tag, substance (cf. <mat>, terra, choça, magma)',
        '<cm-h>': 'human-made substance (cf. <mat>, cemento)',
        '<cm-chem>': 'chemical substance, also biological (acetileno, amônio, anilina, bilirrubina',
        '<cm-gas>': 'gas substance (so far few: argônio, overlap with. <cm-chem> and <cm>)',
        '<cm-liq>': 'liquid substance (azeite, gasolina, plasma, overlap with <food> and <cm-rem>)',
        '<cm-rem>': 'remedy (medical or hygiene, antibiótico, canabis, quinina, part of <cm-h>, overlap with <cm-chem>)',
        },
    'Materials':
        {
        '<mat>': 'material (argila, bronze, granito, cf. <cm>)',
        '<mat-cloth>': 'cloth material (seda, couro, vison, kevlar), cp. <cc-rag>',
        '<cord>': 'cord, string, rope, tape (previously <tool-tie>, arame, fio, fibrila)',
        },
    'Clothing':
        {
        '<cloA>': 'animal clothing (sela, xabraque)',
        '<cloH>': 'human clothing (albornoz, anoraque, babadouro, bermudas)',
        '<cloH-beauty>': 'beauty clothing (e.g. jewelry, diadema, pendente, pulseira)',
        '<cloH-hat>': 'hat (sombrero, mitra, coroa)',
        '<cloH-shoe>': 'shoe (bota, chinela, patim)',
        '<mat-cloth>': 'cloth material (seda, couro, vison, kevlar), cp. <cc-rag>',
        '<clo...>': '(clothing)',
        },
    'Collective':
        {
        '<coll>': 'set,collective (random or systematic collection/compound/multitude of similar but distinct small parts, conjunto, série)',
        '<coll-cc>': 'thing collective, pile (baralho, lanço)',
        '<coll-B>': 'plant-part collective (buquê, folhagem)',
        '<coll-sem>': 'semantic collective, collection (arquivo, repertório)',
        '<coll-tool>': 'tool collective, set (intrumentário, prataria)',
        '<HH>': '(group)',
        '<AA>': '(herd)',
        '<BB>': '(plantation)',
        '<VV>': '(convoy)',
        },
    'Time_Event':
        {
        '<dur>': 'duration noun (test: durar+, implies <unit>, e.g. átimo, mês, hora)',
        '<temp>': 'temporal object, point in time (amanhecer, novilúnio, test: até+, cf. <dur> and <per>)',
        '<event>': 'non-organised event  (-CONTROL, PERFECTIVE, milagre, morte)',
        '<occ>': 'occasion, human/social event (copa do mundo, aniversário, jantar, desfile, cp. unorganized <event>) ',
        '<process>': 'process (-CONTROL, -PERFECTIVE, cp. <event>, balcanização, convecção, estagnação)',
        '<act...>': '',
        '<activity>': '',
        '<history>': '(EFEMERIDE) one-time [historical] occurrence',
        '<date>': '(DATA) date',
        '<hour>': '(HORA) hour',
        '<period>': '(PERIODO) period',
        '<cyclic>': '(CICLICO) cyclic time expression',
        '<month>': 'month noun/name (agosto, julho, part of <temp>)',
        '<per>': 'period of time (prototypical test: durante, e.g. guerra, década, cf. <dur> and <temp>)',
        },
    'Feature':
        {
        '<f>': 'feature/property, umbrella tag (problematicidade, proporcionalidade)',
        '<f-an>': 'anatomical "local" feature, includes countables, e.g. barbela, olheiras)',
        '<f-c>': 'general countable feature (vestígio, laivos, vinco)',
        '<f-h>': 'human physical feature, not countable (lindura, compleição, same as <f-phys-h>, cp. anatomical local features <f-an>)',
        '<f-phys-h>': '',
        '<f-psych>': 'human psychological feature (passionalidade, pavonice, cp. passing states <state-h>)',
        '<f-q>': 'quantifiable feature (e.g. circunferência, calor, DanGram-s <f-phys> covers both <f> and <f-q>)',
        '<f-phys>': '',
        '<f-right>': 'human social feature (right or duty): e.g. copyright, privilégio, imperativo legal)',
        '<state>': '',
        '<state-h>': '(human state)',
        },
    'Food':
        {
        '<food>': 'natural/simplex food (aveia, açúcar, carne, so far including <spice>)',
        '<food-c>': 'countable food (few: ovo, dente de alho, most are <fruit> or <food-c-h>)',
        '<food-h>': 'human-prepared/complex culinary food (caldo verde, lasanha)',
        '<food-c-h>': 'culinary countable food (biscoito, enchido, panetone, pastel)',
        '<drink>': 'drink (cachaça, leite, guaraná, moca)',
        '<fruit>': 'fruit, berry, nut (still mostly marked as <food-c>, abricote, amora, avelã, cebola)',
        '<spice>': 'condiments, pepper',
        },
    'Part':
        {
        '<part>': 'distinctive or functional part (ingrediente, parte, trecho)',
        '<part-build>': 'structural part of building or vehicle (balustrada, porta, estai)',
        '<piece>': 'indistinctive (little) piece (pedaço, raspa)',
        '<cc-handle>': '',
        '<Ltip>': '',
        },
    'Perception':
        {
        '<percep-f>': 'what you feel (senses or sentiment, pain, e.g. arrepio, aversão, desagrado, cócegas, some overlap with <state-h>)',
        '<percep-l>': 'sound (what you hear, apitadela, barrulho, berro, crepitação)',
        '<percep-o>': 'olfactory impression (what you smell, bafo, chamuscom fragrância)',
        '<percep-t>': 'what you taste (PALAVRAS: not implemented)',
        '<percep-w>': 'visual impression (what you see, arco-iris, réstia, vislumbre)',
        },
    'Semantic Product':
        {
        '<sem>': 'semiotic artifact, work of art, umbrella tag (all specified in PALAVRAS)',
        '<sem-c>': 'cognition product (concept, plan, system, conjetura, esquema, plano, prejuízo)',
        '<sem-l>': 'listen-work (music, cantarola, prelúdio, at the same time <genre>: bossa nova)',
        '<sem-nons>': 'nonsense, rubbish (implies <sem-s>, galimatias, farelório)',
        '<sem-r>': 'read-work (biografia, dissertação, e-mail, ficha cadastral)',
        '<sem-s>': 'speak-work (palestra, piada, exposto)',
        '<sem-w>': 'watch-work (filme, esquete, mininovela)',
        '<ac-s>': '(speach act)',
        '<talk>': '',
        },
    'Disease':
        {
        '<sick>': 'disease (acne, AIDS, sida, alcoolismo, cp. <Hsick>)',
        '<Hsick>': '',
        '<sick-c>': 'countable disease-object (abscesso, berruga, cicatriz, gangrena)',
        },
    'State-of-affairs':
        {
        '<sit>': 'psychological situation or physical state of affairs (reclusão, arruaça, ilegalidade, more complex and more "locative" than <state> and <state-h>',
        '<state>': 'state (of something, otherwise <sit>), abundância, calma, baixa-mar, equilíbrio',
        '<state-h>': 'human state (desamparo, desesperança, dormência, euforia, febre',
        '<f-psych>': '',
        '<f-phys-h>': '',
        },
    'Sport':
        {
        '<sport>': 'sport (capoeira, futebol, golfe, also <activity> and <domain>)',
        },
    'Tool':
        {
        '<tool>': 'tool, umbrella tag (abana-moscas, lápis, computador, maceta, "handable", cf. <mach>)',
        '<tool-cut>': 'cutting tool, knife (canivete, espada)',
        '<tool-gun>': 'shooting tool, gun (carabina, metralhadora, helicanão, in Dangram: <tool-shoot>)',
        '<tool-mus>': 'musical instrument (clavicórdio, ocarina, violão)',
        '<tool-sail>': 'sailing tool, sail (vela latina, joanete, coringa)',
        '<mach>': 'machine (complex, usually with moving parts, betoneira, embrulhador, limpa-pratos, cp. <tool>)',
        '<tube>': 'tube object (cânula, gasoduto, zarabatana, shape-category, typically with another category, like <an> or <tool>)',
        },
    'Unit':
        {
        '<unit>': 'unit noun (always implying <num+>, implied by <cur> and <dur>, e.g. caloria, centímetro, lúmen))',
        },
    'Weather':
        {
        '<wea>': 'weather (states), umbrella tag (friagem, bruma)',
        '<wea-c>': 'countable weather phenomenon (nuvem, tsunami)',
        '<wea-rain>': 'rain and other precipitation (chuvisco, tromba d-água, granizo)',
        '<wea-wind>': 'wind, storm (brisa, furacão)',
        },
    'Person':
        {
        '<hum>': '(INDIVIDUAL) person name (cp. <H>)',
        '<official>': '(CARGO) official function (~ cp. <Htitle> and <Hprof>)',
        '<member>': '(MEMBRO) member',
        },
    'Organization_Group':
        {
        '<admin>': '(ADMINISTRACAO, ORG.) administrative body (government, town administration etc.)',
        '<org>': '(INSTITUICAO/EMPRESA) commercial or non-commercial, non-administrative non-party organisations (not place-bound, therefore not the same as <Linst>)',
        '<inst>': '(EMPRESA) organized site (e.g. restaurant, cp. <Linst>)',
        '<media>': '(EMPRESA) media organisation (e.g. newspaper, tv channel)',
        '<party>': '(INSTITUICAO) political party',
        '<suborg>': '(SUB) organized part of any of the above',
        '<company>': 'currently unsupported: (EMPRESA) company (not site-bound, unlike <inst>, now fused with. <org>)',
        },
    'Group':
        {
        '<groupind>': '(GROUPOIND) people, family',
        '<groupofficial>': '(GROUPOCARGO) board, government (not fully implemented)',
        '<grouporg>': 'currently unsupported (GROUPOMEMBRO) club, e.g. football club (now fused with <org>)',
        },
    'Place':
        {
        '<top>': '(GEOGRAFICO) geographical location (cp. <Ltop>)',
        '<civ>': '(ADMINISTRACAO, LOC.) civitas (country, town, state, cp. <Lciv>)',
        '<address>': '(CORREIO) address (including numbers etc.)',
        '<site>': '(ALARGADO) functional place (cp. <Lh>)',
        '<virtual>': '(VIRTUAL) virtual place',
        '<astro>': '(OBJECTO) astronomical place (in HAREM object, not place)',
        '<road>': 'suggested (ALARGADO) roads, motorway (unlike <address>)',
        },
    'Work_of_Art':
        {
        '<tit>': '(REPRODUZIDO) [title of] reproduced work, copy',
        '<pub>': '(PUBLICACAO) [scientific] publication',
        '<product>': '(PRODUTO) product brand',
        '<V>': '(PRODUTO) vehicle brand (cp. <V>, <Vair>, <Vwater>)',
        '<artwork>': '(ARTE) work of art',
        '<pict>': 'picture (combination of <cc>, <sem-w> and <L>, caricatura, cintilograma, diapositivo)',
        },
    'Colours':
        {
        '<col>': 'colours',
        },
    'Numeric_and_Math':
        {
        '<quantity>': '(QUANTIDADE) simple measuring numeral',
        '<prednum>': '(CLASSIFICADO) predicating numeral',
        '<currency>': '(MOEDA) currency name (also marked on the unit)',
        '<geom>': 'geometry noun (circle, shape, e.g. losango, octógono, elipse)',
        '<geom-line>': 'line (few: linha, percentil, curvas isobáricas)',
        },
    'Modifying_Adjectives':
        {
        '<jh>': 'adjective modifying human noun',
        '<jn>': 'adjective modifying inanimate noun ',
        '<ja>': 'adjective modifying animal',
        '<jb>': 'adjective modifying plant',
        '<col>': 'color adjective',
        '<nat>': 'nationality adjective (also: from a certain town etc.)',
        '<attr>': '(human) attributive adjective (not fully implemented, cp. <Hattr>, e.g. "um presidente COMUNISTA")',
        },
    'Verbs_related_human_things':
        {
        '<vH>': 'verb with human subject',
        '<vN>': 'verb with inanimate subject',
        },
}


angle_brackets_contents = re.compile('(<[a-zA-Z]*>)')

class SemanticTagger(PyPLNTask):
    """Semantic Tagger"""

    def process(self, document):
        if not document['palavras_raw_ran']:
            # If palavras didn't run, just ignore this document
            return {}

        lines = document['palavras_raw'].split('\n')
        tagged_entities = {}
        for line in lines:
            if line.startswith('$') or not line.strip() or \
               line.strip() == '</s>':
                continue
            word = line.split()[0]
            word_sem_tags = angle_brackets_contents.findall(line.strip())
            is_tagged = False
            for tag in word_sem_tags:
                for category, subcategories in SEMANTIC_TAGS.items():
                    if tag in subcategories:
                        tagged_entities.setdefault(category, []).append(word)
                        is_tagged = True
            if not is_tagged:
                tagged_entities.setdefault('Non_Tagged', []).append(word)
        return {'semantic_tags': tagged_entities}
