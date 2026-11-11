/* Plan d'action personnalisé (produit payant). Tout est calculé dans le navigateur.
   Montants 2026 : fiche CNSA APA au 1er janvier 2026, service-public.gouv.fr. */
(function () {
  var MTP = 1288.13, PLAF = {1: 2080.33, 2: 1682.30, 3: 1215.99, 4: 811.52};
  var eur = function (x) { return Math.round(x).toLocaleString('fr-FR') + ' €'; };
  var num = function (v) { v = parseFloat(String(v || '').replace(/\s/g, '').replace(',', '.')); return isNaN(v) ? 0 : v; };
  var get = function (k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } };
  var set = function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
  var E = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]; }); };

  function partAPA(A, R) {
    var S = MTP, lo = 0.725 * S, hi = 2.67 * S;
    if (R <= lo) return 0; if (R > hi) return 0.9 * A;
    var x = (R - lo) / (hi - lo), b = 0.9 * x;
    var A1 = Math.min(A, 0.317 * S), A2 = Math.max(0, Math.min(A, 0.498 * S) - 0.317 * S), A3 = Math.max(0, A - 0.498 * S);
    return A1 * b + A2 * b * (1 - 0.6 * (1 - x)) + A3 * b * (1 - 0.8 * (1 - x));
  }
  function apa(gir, R) { var a = PLAF[gir] - partAPA(PLAF[gir], R); return a < 36.93 ? 0 : a; }

  var p = new URLSearchParams(location.search);
  if (/^cs_/.test(p.get('s') || '')) { set('amp-paid', {s: p.get('s'), t: Date.now()}); history.replaceState(null, '', '/mon-plan/'); }
  var paid = get('amp-paid'), q = get('amp-quiz');
  var vente = document.getElementById('plan-vente'), form = document.getElementById('plan-form'), out = document.getElementById('plan-out');
  if (!paid) return;
  vente.hidden = true;
  if (!q) { out.innerHTML = '<h1>Votre plan d’action</h1><p>Pour préparer votre plan, répondez d’abord aux 5 questions du <a href="/quelles-aides/">questionnaire</a> sur ce même appareil, puis revenez sur cette page. Votre accès est conservé.</p>'; return; }
  var info = get('amp-plan-info');
  if (info) return render(info);
  form.hidden = false;
  var f = document.getElementById('pf');
  f.addEventListener('submit', function () {
    if (!f.checkValidity()) { f.reportValidity(); return; }
    info = {dep: f.dep.value.trim(), res: num(f.res.value), couple: f.couple.checked, log: f.log.value, prenom: f.prenom.value.trim()};
    set('amp-plan-info', info); form.hidden = true; render(info);
  });

  function render(i) {
    var nom = i.prenom ? E(i.prenom) : 'votre parent', R = i.couple ? i.res / 1.7 : i.res;
    var dom = q.lieu !== 'ehpad', age = +q.age, auto = +q.auto, gir14 = auto <= 3;
    var dep = encodeURIComponent(i.dep), d = new Date(), j = function (n) { var x = new Date(d); x.setDate(x.getDate() + n); return x.toLocaleDateString('fr-FR', {day: 'numeric', month: 'long', year: 'numeric'}); };
    var A = [], total = 0;
    if (gir14) {
      var g = auto === 1 ? [2, 1] : [4, 3], lo = apa(g[0], R), hi = apa(g[1], R); total += lo;
      A.push({t: 'APA à domicile' + (dom ? '' : ' (en établissement)'), m: dom ? (lo === hi ? eur(lo) : eur(lo) + ' à ' + eur(hi)) + ' par mois (GIR ' + g[0] + ' ou ' + g[1] + ')' : 'Finance une partie du tarif dépendance de l’établissement',
        ou: 'Conseil départemental (' + E(i.dep) + '), par le formulaire unique cerfa n°16301 « Demande d’aides à l’autonomie à domicile », sur papier ou sur demande-autonomie.gouv.fr si votre département le propose.',
        pieces: ['Pièce d’identité de ' + nom, 'Dernier avis d’imposition', 'RIB', 'Avis de taxe foncière si ' + nom + ' est propriétaire de biens non loués'],
        delais: 'Accusé de réception sous 10 jours, visite d’évaluation à domicile, décision au plus tard 2 mois après le dossier complet. L’APA est due à partir du dossier complet : déposez-le le plus tôt possible.', u: '/apa/demande/', prio: 3});
    }
    if (auto === 1 && gir14) A.push({t: 'Carte mobilité inclusion (stationnement et invalidité)', m: 'Attribuée sans passer par la MDPH avec l’APA en GIR 1 ou 2',
      ou: 'Demandée en même temps que l’APA ; la carte arrive environ 10 jours après l’envoi de la photo.', pieces: ['Photo d’identité'], delais: 'Après la décision d’APA.', u: '/carte-mobilite-inclusion/', prio: 2});
    if (age >= 65) { var plaf = i.couple ? 1620.18 : 1043.59, as = Math.max(0, plaf - i.res); if (as > 0) { total += as; A.push({t: 'ASPA (minimum vieillesse)', m: 'Environ ' + eur(as) + ' par mois', ou: 'La caisse qui verse sa retraite (Carsat ou MSA), avec le formulaire de demande d’ASPA de cette caisse.', pieces: ['Justificatifs de ressources des 3 ou 12 derniers mois', 'Pièce d’identité', 'RIB'], delais: 'Attention : l’ASPA peut être récupérée sur la succession au-delà de 108 586,14 € d’actif net (décès en 2026).', u: '/aspa/', prio: 3}); } }
    if (dom) A.push({t: 'Crédit d’impôt de 50 % sur l’aide à domicile', m: 'La moitié des dépenses restant à charge, jusqu’à 12 000 € de dépenses par an (plafond majoré selon l’âge)',
      ou: 'Sur la déclaration de revenus, au printemps, pour les dépenses de l’année précédente.', pieces: ['Attestations annuelles du service d’aide à domicile', 'Montant des aides reçues (APA) à déduire'], delais: 'Prochaine déclaration : printemps ' + (d.getFullYear() + 1) + '. Conservez toutes les factures dès maintenant.', u: '/aide-a-domicile/', prio: 2});
    if (dom && (age >= 70 || gir14) && i.log !== 'autre') A.push({t: 'MaPrimeAdapt (adaptation du logement)', m: '50 % ou 70 % des travaux, sur 22 000 € HT de travaux au maximum, selon les revenus',
      ou: 'Sur france-renov.gouv.fr, avec un assistant à maîtrise d’ouvrage (AMO) obligatoire.' + (i.log === 'loc' ? ' Locataire : il faut l’accord écrit du propriétaire.' : ''), pieces: ['Dernier avis d’imposition', 'Devis des travaux', 'Justificatif de propriété ou accord du propriétaire'], delais: 'Ne signez aucun devis et ne commencez aucun travaux avant l’accord de l’Anah.', u: '/maprimeadapt/', prio: 2});
    if (age >= 75 && dom) A.push({t: 'Sortir Plus (Agirc-Arrco)', m: 'Un accompagnateur pour les sorties, pris en charge par la caisse dans la limite d’un plafond annuel', ou: 'Appelez le 0 971 090 971 (lundi au vendredi, 8h30 à 18h30).', pieces: ['Numéro de sécurité sociale de ' + nom], delais: 'Appelez environ une semaine avant le premier besoin, puis 2 jours avant chaque sortie.', u: '/sortir-plus/', prio: 1});
    if (dom && auto <= 5) A.push({t: 'Téléassistance', m: 'Souvent aidée par le département ou la commune, parfois gratuite avec l’APA', ou: 'Service téléassistance du conseil départemental (' + E(i.dep) + ') ou CCAS de la mairie.', pieces: ['Coordonnées de 2 ou 3 proches à prévenir'], delais: 'Installation en quelques jours en général.', u: '/teleassistance/', prio: 1});
    if (!dom) {
      A.push({t: 'Réduction d’impôt pour les frais d’EHPAD', m: '25 % des frais de dépendance et d’hébergement, 2 500 € par an au maximum', ou: 'Déclaration de revenus de ' + nom + ', au printemps.', pieces: ['Facture annuelle de l’EHPAD'], delais: 'Printemps ' + (d.getFullYear() + 1) + '.', u: '/ehpad-prix-aides/', prio: 2});
      if (R < 3439) A.push({t: 'Aide sociale à l’hébergement (ASH)', m: 'Prend en charge ce que ' + nom + ' ne peut pas payer ; il lui reste au moins 10 % de ses revenus (125 € minimum)', ou: 'Dossier à déposer au CCAS ou à la mairie, transmis au département.', pieces: ['Justificatifs de ressources', 'Revenus des enfants (obligés alimentaires)', 'Contrat de séjour de l’établissement habilité'], delais: 'À demander dans les 2 mois qui suivent l’entrée en établissement.', u: '/aide-sociale-hebergement/', prio: 3});
    }
    if (q.vous === 'sal' && gir14) A.push({t: 'Votre congé de proche aidant et l’AJPA', m: '66,64 € par jour d’AJPA en 2026, 22 jours par mois au maximum', ou: 'Votre employeur (lettre ci-dessous), puis la CAF ou la MSA pour l’AJPA.', pieces: ['Décision d’APA de ' + nom, 'Déclaration sur l’honneur du lien familial', 'Déclaration sur l’honneur des congés déjà pris'], delais: 'Prévenez l’employeur au moins 1 mois avant, sauf urgence.', u: '/conge-proche-aidant/', prio: 2});
    A.sort(function (a, b) { return b.prio - a.prio; });

    var h = '<h1>Le plan d’action pour ' + nom + '</h1><p class="chapo">Établi le ' + j(0) + ', département ' + E(i.dep) + '. Montants 2026 estimés à partir de vos réponses : c’est l’organisme qui verse chaque aide qui décide.</p>';
    h += '<div class="plan-total"><p class="lab">Aides financières estimées</p><p class="big">' + (total ? eur(total) + ' <small>par mois au minimum</small>' : 'Voir chaque aide ci-dessous') + '</p><p>Plus les avantages fiscaux et les services aidés listés ci-dessous.</p></div>';
    h += '<h2>Votre calendrier</h2><ol class="etapes">' +
      (gir14 ? '<li><b>Avant le ' + j(7) + '</b> : déposez le dossier APA (cerfa n°16301). Chaque semaine d’attente est une semaine d’aide en moins.</li>' : '') +
      (!dom ? '<li><b>Dans les 2 mois après l’entrée en EHPAD</b> : déposez la demande d’aide sociale au CCAS si les ressources ne suffisent pas.</li>' : '') +
      (q.vous === 'sal' && gir14 ? '<li><b>1 mois avant</b> la date voulue : envoyez la lettre de congé de proche aidant à votre employeur.</li>' : '') +
      '<li><b>Dès maintenant</b> : rassemblez les pièces de chaque aide (liste ci-dessous) dans une même pochette.</li>' +
      '<li><b>Au printemps ' + (d.getFullYear() + 1) + '</b> : déclarez les dépenses d’aide à domicile ou d’EHPAD pour le crédit ou la réduction d’impôt.</li></ol>';
    h += '<h2>Les aides, dans l’ordre</h2>';
    A.forEach(function (a, k) {
      h += '<section class="plan-aide"><h3>' + (k + 1) + '. ' + a.t + '</h3><p class="m">' + a.m + '</p><p><b>Où et comment :</b> ' + a.ou + '</p><p><b>Pièces à rassembler :</b></p><ul>' + a.pieces.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul><p><b>Délais :</b> ' + a.delais + '</p><p><a href="' + a.u + '">Le guide complet →</a></p></section>';
    });
    h += '<h2>Vos lettres prêtes à envoyer</h2><p>Complétez les crochets, signez, et envoyez en recommandé avec accusé de réception.</p>';
    if (gir14) h += lettre('Recours contre une décision d’APA', '[Prénom Nom de votre parent]\n[Adresse]\n\nMonsieur le Président du conseil départemental\n[Adresse du conseil départemental]\n\nObjet : recours contre la décision d’APA du [date de la décision], dossier n° [numéro]\n\nMonsieur le Président,\n\nJe conteste la décision du [date] relative à ma demande d’allocation personnalisée d’autonomie, que j’ai reçue le [date de réception]. [Expliquez en quelques phrases : refus, GIR attribué, montant du plan d’aide jugé insuffisant, et pourquoi : besoins réels au quotidien, aggravation de l’état de santé, éléments non pris en compte lors de la visite.]\n\nJe vous demande de bien vouloir réexaminer mon dossier et, si nécessaire, de procéder à une nouvelle évaluation à domicile. Vous trouverez ci-joint [pièces : certificat médical récent, copie de la décision].\n\nJe vous prie d’agréer, Monsieur le Président, l’expression de ma considération distinguée.\n\n[Signature]');
    if (gir14) h += lettre('Demande de révision de l’APA (aggravation)', '[Prénom Nom de votre parent]\n[Adresse]\n\nMonsieur le Président du conseil départemental\n[Adresse]\n\nObjet : demande de révision de l’APA, dossier n° [numéro]\n\nMonsieur le Président,\n\nJe bénéficie de l’allocation personnalisée d’autonomie depuis le [date]. Ma situation s’est aggravée : [décrivez les changements : chute, hospitalisation, besoin d’aide nouveau pour la toilette, les repas, la nuit]. Je vous demande une nouvelle évaluation de ma perte d’autonomie et la révision de mon plan d’aide.\n\nVous trouverez ci-joint [certificat médical récent].\n\nJe vous prie d’agréer, Monsieur le Président, l’expression de ma considération distinguée.\n\n[Signature]');
    if (q.vous === 'sal' && gir14) h += lettre('Demande de congé de proche aidant à votre employeur', '[Votre prénom et nom]\n[Votre adresse]\n\n[Nom de l’employeur]\n[Adresse]\n\nObjet : demande de congé de proche aidant\n\nMadame, Monsieur,\n\nJe vous informe de ma volonté de suspendre mon contrat de travail au titre du congé de proche aidant, à compter du [date, au moins 1 mois après l’envoi], pour une durée de [durée, 3 mois au plus], afin d’accompagner [lien : ma mère, mon père], [prénom nom], qui présente une perte d’autonomie. [Si besoin : je souhaite fractionner ce congé / le prendre sous forme de temps partiel.]\n\nVous trouverez ci-joint une déclaration sur l’honneur de mon lien familial, une déclaration sur l’honneur relative aux congés de proche aidant déjà pris, et la copie de la décision d’APA.\n\nJe vous prie d’agréer, Madame, Monsieur, l’expression de mes salutations distinguées.\n\n[Signature]');
    h += '<h2>Les contacts utiles</h2><ul><li>Conseil départemental et CCAS : <a href="https://lannuaire.service-public.gouv.fr/" rel="noopener" target="_blank">l’annuaire officiel de l’administration</a> (cherchez « conseil départemental ' + E(i.dep) + ' »)</li><li>Point d’information local pour les personnes âgées : <a href="https://www.pour-les-personnes-agees.gouv.fr/annuaire-points-dinformation-et-plateformes-de-repit" rel="noopener" target="_blank">annuaire officiel</a></li><li>Sortir Plus et aides Agirc-Arrco : 0 971 090 971</li></ul>';
    h += '<p class="noprint"><button class="btn" type="button" onclick="window.print()">Enregistrer en PDF ou imprimer</button> <a class="btn sec" href="/quelles-aides/">Refaire le questionnaire</a></p>';
    h += '<p class="note">Ce plan est une aide à la préparation des démarches : les démarches elles-mêmes sont gratuites auprès des organismes. Les montants sont des estimations établies avec les barèmes 2026 ; seul l’organisme qui verse l’aide décide.</p>';
    out.innerHTML = h;
    out.querySelectorAll('.copy').forEach(function (b) { b.onclick = function () { var t = b.parentNode.querySelector('pre').innerText; navigator.clipboard.writeText(t).then(function () { b.textContent = 'Copié'; }); }; });
    if (window.goatcounter) try { goatcounter.count({path: 'plan-affiche', event: true}); } catch (x) {}
  }
  function lettre(t, x) { return '<details class="lettre"><summary>' + t + '</summary><pre>' + E(x) + '</pre><button class="btn sec copy" type="button">Copier la lettre</button></details>'; }
})();
