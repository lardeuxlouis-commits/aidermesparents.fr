/* Calculateurs de aidermesparents.fr : tout se calcule dans le navigateur, rien n'est envoyé.
   Paramètres 2026 : fiche CNSA « Montants applicables à l'APA au 1er janvier 2026 », service-public.gouv.fr. */
(function () {
  var MTP = 1288.13, PLAF = {1: 2080.33, 2: 1682.30, 3: 1215.99, 4: 811.52}, SEUIL_NV = 36.93;
  var eur = function (x) { return x.toLocaleString('fr-FR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' €'; };
  var num = function (v) { v = parseFloat(String(v).replace(/\s/g, '').replace(',', '.')); return isNaN(v) ? 0 : v; };
  var mem = {};
  try { mem = JSON.parse(localStorage.getItem('amp-calc') || '{}'); } catch (e) {}
  var save = function (k, v) { mem[k] = v; try { localStorage.setItem('amp-calc', JSON.stringify(mem)); } catch (e) {} };

  function participationAPA(A, R) {
    var S = MTP, lo = 0.725 * S, hi = 2.67 * S;
    if (R <= lo) return 0;
    if (R > hi) return 0.9 * A;
    var x = (R - lo) / (hi - lo), base = 0.9 * x;
    var A1 = Math.min(A, 0.317 * S), A2 = Math.max(0, Math.min(A, 0.498 * S) - 0.317 * S), A3 = Math.max(0, A - 0.498 * S);
    return A1 * base + A2 * base * (1 - 0.6 * (1 - x)) + A3 * base * (1 - 0.8 * (1 - x));
  }

  var CTA = '<p class="calc-cta">Ce n’est qu’une partie des aides possibles. <a href="/quelles-aides/">Voir toutes les aides de votre parent →</a></p>';

  var W = {
    apa: {
      titre: 'Simulateur : combien d’APA pour votre parent ?',
      html: '<label>Niveau de dépendance (GIR)<select name="gir"><option value="1">GIR 1</option><option value="2">GIR 2</option><option value="3">GIR 3</option><option value="4" selected>GIR 4</option></select></label>' +
        '<label>Ressources mensuelles de votre parent<input name="res" inputmode="decimal" placeholder="ex. 1 400"></label>' +
        '<label class="chk"><input type="checkbox" name="couple"> Il vit en couple (ressources du couple)</label>' +
        '<label>Montant du plan d’aide (laissez vide = plafond du GIR)<input name="plan" inputmode="decimal" placeholder="plafond"></label>',
      calc: function (f) {
        var gir = +f.gir.value, R = num(f.res.value), couple = f.couple.checked;
        save('res', f.res.value); save('gir', f.gir.value); save('couple', couple);
        var Rr = couple ? R / 1.7 : R, A = num(f.plan.value) || PLAF[gir];
        A = Math.min(A, PLAF[gir]);
        var P = participationAPA(A, Rr), apa = A - P;
        if (apa < SEUIL_NV) apa = 0;
        var t = A ? Math.round(P / A * 100) : 0;
        return '<p class="big">' + (apa ? eur(apa) + ' <small>d’APA par mois</small>' : 'Pas d’APA versée') + '</p>' +
          '<ul><li>Plan d’aide retenu : ' + eur(A) + ' (plafond ' + eur(PLAF[gir]) + ' en GIR ' + gir + ')</li>' +
          '<li>Participation de votre parent : ' + eur(P) + ' par mois (' + t + ' %)</li>' +
          (couple ? '<li>Ressources prises en compte : ' + eur(Rr) + ' (ressources du couple divisées par 1,7)</li>' : '') +
          '</ul><p class="note">Estimation selon le barème national 2026. Le montant réel dépend du plan d’aide décidé par le département après la visite d’évaluation.</p>';
      }
    },
    aspa: {
      titre: 'Simulateur : montant d’ASPA possible',
      html: '<label>Ressources mensuelles actuelles (retraites et autres revenus)<input name="res" inputmode="decimal" placeholder="ex. 750"></label>' +
        '<label class="chk"><input type="checkbox" name="couple"> En couple (ressources du couple)</label>',
      calc: function (f) {
        var R = num(f.res.value), c = f.couple.checked, plaf = c ? 1620.18 : 1043.59;
        save('res', f.res.value); save('couple', c);
        var a = Math.max(0, plaf - R);
        return '<p class="big">' + (a ? eur(a) + ' <small>par mois</small>' : 'Pas d’ASPA') + '</p><ul><li>Plafond 2026 : ' + eur(plaf) + ' par mois ' + (c ? 'pour un couple' : 'pour une personne seule') + '</li><li>L’ASPA complète les ressources jusqu’à ce plafond.</li></ul>' +
          '<p class="note">Estimation. La caisse de retraite tient compte de toutes les ressources des 3 derniers mois (ou des 12 derniers).</p>';
      }
    },
    credit: {
      titre: 'Calculateur : votre crédit d’impôt pour l’aide à domicile',
      html: '<label>Dépenses d’aide à domicile sur l’année<input name="dep" inputmode="decimal" placeholder="ex. 6 000"></label>' +
        '<label>Aides reçues pour ces dépenses (APA, caisse de retraite…)<input name="aides" inputmode="decimal" placeholder="ex. 2 400"></label>' +
        '<label>Personnes de plus de 65 ans dans le foyer<select name="p65"><option value="0">Aucune</option><option value="1" selected>1</option><option value="2">2</option></select></label>' +
        '<label class="chk"><input type="checkbox" name="inv"> Titulaire d’une carte d’invalidité à 80 % (plafond 20 000 €)</label>',
      calc: function (f) {
        var net = Math.max(0, num(f.dep.value) - num(f.aides.value));
        var plaf = f.inv.checked ? 20000 : Math.min(15000, 12000 + 1500 * +f.p65.value);
        var c = 0.5 * Math.min(net, plaf);
        return '<p class="big">' + eur(c) + ' <small>de crédit d’impôt</small></p><ul><li>Dépenses restant à votre charge : ' + eur(net) + '</li><li>Plafond retenu : ' + eur(plaf) + '</li><li>Coût réel après crédit : ' + eur(net - c) + '</li></ul>' +
          '<p class="note">C’est un crédit d’impôt : il est remboursé même si vous n’êtes pas imposable. Plafond majoré la première année d’emploi direct.</p>';
      }
    },
    ehpad: {
      titre: 'Calculateur : reste à charge en EHPAD',
      html: '<label>Facture mensuelle de l’EHPAD (hébergement + dépendance)<input name="fact" inputmode="decimal" placeholder="ex. 2 600"></label>' +
        '<label>Aide au logement (APL ou ALS) par mois<input name="apl" inputmode="decimal" placeholder="ex. 150"></label>' +
        '<label>APA en établissement versée à l’EHPAD par mois<input name="apa" inputmode="decimal" placeholder="ex. 300"></label>' +
        '<label>Ressources mensuelles de votre parent<input name="res" inputmode="decimal" placeholder="ex. 1 500"></label>',
      calc: function (f) {
        var fact = num(f.fact.value), apl = num(f.apl.value), apa = num(f.apa.value), R = num(f.res.value);
        save('res', f.res.value);
        var net = Math.max(0, fact - apl - apa), red = Math.min(0.25 * Math.min(net * 12, 10000), 2500) / 12;
        var reste = net - red, manque = reste - R;
        return '<p class="big">' + eur(reste) + ' <small>par mois après aides</small></p><ul><li>Après APL et APA : ' + eur(net) + '</li><li>Réduction d’impôt (25 %, 2 500 € par an au maximum) : environ ' + eur(red) + ' par mois, si votre parent est imposable</li>' +
          (R ? '<li>' + (manque > 0 ? 'Il manque environ ' + eur(manque) + ' par mois par rapport à ses ressources : regardez <a href="/aide-sociale-hebergement/">l’aide sociale à l’hébergement</a>.' : 'Ses ressources couvrent la facture.') + '</li>' : '') +
          '</ul><p class="note">Estimation. Le tarif exact figure dans le contrat de séjour de l’établissement.</p>';
      }
    },
    ajpa: {
      titre: 'Calculateur : votre allocation de proche aidant (AJPA)',
      html: '<label>Jours complets de congé par mois<input name="j" inputmode="numeric" placeholder="ex. 8"></label><label>Demi-journées par mois<input name="d" inputmode="numeric" placeholder="ex. 2"></label>',
      calc: function (f) {
        var j = Math.max(0, Math.round(num(f.j.value))), d = Math.max(0, Math.round(num(f.d.value)));
        var jours = j + d / 2, cap = Math.min(jours, 22), m = Math.min(j, 22) * 66.64 + Math.max(0, Math.min(d, (22 - Math.min(j, 22)) * 2)) * 33.32;
        return '<p class="big">' + eur(m) + ' <small>par mois</small></p><ul><li>66,64 € par jour et 33,32 € par demi-journée en 2026</li><li>22 jours au maximum par mois, 66 jours par personne aidée</li>' + (jours > 22 ? '<li>Au-delà de 22 jours dans le mois, l’AJPA n’est pas versée.</li>' : '') + '</ul><p class="note">Montant net de prélèvements sociaux à vérifier sur votre notification CAF ou MSA.</p>';
      }
    },
    c2s: {
      titre: 'Simulateur : la mutuelle gratuite (complémentaire santé solidaire)',
      html: '<label>Personnes dans le foyer<select name="n"><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select></label>' +
        '<label>Ressources du foyer sur les 12 derniers mois<input name="r" inputmode="decimal" placeholder="ex. 13 000"></label>' +
        '<label>Âge de votre parent<select name="age"><option value="60">60 à 69 ans</option><option value="70" selected>70 ans ou plus</option><option value="0">moins de 60 ans</option></select></label>',
      calc: function (f) {
        var n = +f.n.value, r = num(f.r.value), G = [0, 10421, 15632, 18758, 21885], P = [0, 14069, 21103, 25324, 29544];
        var g = n <= 4 ? G[n] : G[4] + 4169 * (n - 4), pay = n <= 4 ? P[n] : P[4] + 5628 * (n - 4), age = +f.age.value;
        var cout = age >= 70 ? 30 : age >= 60 ? 25 : 0;
        if (r <= g) return '<p class="big">Gratuite</p><ul><li>Plafond 2026 pour ' + n + ' personne' + (n > 1 ? 's' : '') + ' : ' + eur(g) + ' par an</li><li>La complémentaire santé solidaire rembourse comme une bonne mutuelle, sans cotisation.</li></ul><p class="note">Estimation. La caisse d’assurance maladie vérifie les ressources des 12 derniers mois.</p>';
        if (r <= pay) return '<p class="big">' + (cout ? eur(cout) + ' <small>par mois et par personne</small>' : 'Payante') + '</p><ul><li>Vos ressources sont entre ' + eur(g) + ' et ' + eur(pay) + ' : la C2S est payante, à un prix fixé selon l’âge</li></ul><p class="note">Estimation, montant selon l’âge de chaque personne couverte.</p>';
        return '<p class="big">Pas de C2S</p><ul><li>Les ressources dépassent ' + eur(pay) + ' par an pour ' + n + ' personne' + (n > 1 ? 's' : '') + '.</li><li>Regardez plutôt <a href="/mutuelle-senior/">comment bien choisir une mutuelle senior</a>.</li></ul>';
      }
    },
    mpa: {
      titre: 'Simulateur : MaPrimeAdapt pour adapter le logement',
      html: '<label>Personnes dans le foyer<select name="n"><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option></select></label>' +
        '<label>Revenu fiscal de référence (dernier avis d’impôt)<input name="r" inputmode="decimal" placeholder="ex. 19 000"></label>' +
        '<label class="chk"><input type="checkbox" name="idf"> Le logement est en Île-de-France</label>' +
        '<label>Situation<select name="s"><option value="70">70 ans ou plus</option><option value="60">60 à 69 ans avec un GIR (perte d’autonomie)</option><option value="h">Taux d’incapacité d’au moins 50 %</option><option value="0">Aucune de ces situations</option></select></label>',
      calc: function (f) {
        if (f.s.value === '0') return '<p class="big">Non éligible</p><ul><li>MaPrimeAdapt est réservée aux 70 ans et plus, aux 60 à 69 ans classés en GIR, et aux personnes ayant au moins 50 % d’incapacité.</li></ul>';
        var n = +f.n.value, r = num(f.r.value), idf = f.idf.checked;
        var TM = idf ? [0, 24031, 35270, 42357, 49455, 56580] : [0, 17363, 25393, 30540, 35676, 40835], M = idf ? [0, 29253, 42933, 51564, 60208, 68877] : [0, 22259, 32553, 39148, 45735, 52348];
        var t = r <= TM[n] ? 0.7 : r <= M[n] ? 0.5 : 0;
        if (!t) return '<p class="big">Revenus trop élevés</p><ul><li>Le plafond « modestes » est de ' + eur(M[n]) + ' pour ' + n + ' personne' + (n > 1 ? 's' : '') + (idf ? ' en Île-de-France' : ' hors Île-de-France') + '.</li><li>Les caisses de retraite et certaines communes ont d’autres aides : voir <a href="/maprimeadapt/">le guide</a>.</li></ul>';
        return '<p class="big">' + Math.round(t * 100) + ' % <small>des travaux, jusqu’à ' + eur(22000 * t) + ' d’aide</small></p><ul><li>Profil « ' + (t === 0.7 ? 'très modestes' : 'modestes') + ' » : plafond de travaux de 22 000 € HT</li><li>Un assistant à maîtrise d’ouvrage (AMO) est obligatoire avant le dépôt sur France Rénov’</li></ul><p class="note">Estimation selon les plafonds 2026. Ne commencez aucun travaux avant l’accord de l’Anah.</p>';
      }
    },
    apaetab: {
      titre: 'Simulateur : l’APA en EHPAD',
      html: '<label>Tarif dépendance du GIR de votre parent (par jour)<input name="a" inputmode="decimal" placeholder="ex. 22,60"></label>' +
        '<label>Tarif dépendance GIR 5-6 de l’établissement (par jour)<input name="t" inputmode="decimal" placeholder="ex. 6,10"></label>' +
        '<label>Ressources mensuelles de votre parent<input name="res" inputmode="decimal" placeholder="ex. 1 600"></label>',
      calc: function (f) {
        var J = 30.42, A = num(f.a.value) * J, T = num(f.t.value) * J, R = num(f.res.value), S = MTP;
        save('res', f.res.value);
        var P = R < 2.21 * S ? T : R <= 3.4 * S ? T + (A - T) * (R - 2.21 * S) / (1.19 * S) * 0.8 : T + (A - T) * 0.8;
        var apa = Math.max(0, A - P);
        return '<p class="big">' + eur(apa) + ' <small>d’APA par mois, versés à l’EHPAD</small></p><ul><li>Tarif dépendance du GIR : ' + eur(A) + ' par mois</li><li>Reste à la charge de votre parent sur la dépendance : ' + eur(P) + ' par mois</li><li>' + (R < 2.21 * S ? 'Sous ' + eur(2.21 * S) + ' de ressources, il ne paie que le tarif GIR 5-6.' : 'Au-delà de ' + eur(2.21 * S) + ' de ressources, sa participation augmente progressivement.') + '</li></ul><p class="note">Barème national 2026 (fiche CNSA). Les tarifs de l’établissement figurent dans son contrat de séjour ou sur pour-les-personnes-agees.gouv.fr.</p>';
      }
    }
  };

  document.querySelectorAll('[data-calc]').forEach(function (box) {
    var w = W[box.getAttribute('data-calc')]; if (!w) return;
    box.innerHTML = '<p class="lab">Calculateur gratuit</p><h2 class="ct">' + w.titre + '</h2><form class="calc-f">' + w.html + '<button class="btn" type="submit">Calculer</button></form><div class="calc-r" aria-live="polite"></div>' + CTA;
    var f = box.querySelector('form'), out = box.querySelector('.calc-r');
    if (f.res && mem.res) f.res.value = mem.res;
    if (f.gir && mem.gir) f.gir.value = mem.gir;
    if (f.couple && mem.couple) f.couple.checked = true;
    var run = function (e) { if (e) e.preventDefault(); out.innerHTML = w.calc(f); if (window.goatcounter) try { goatcounter.count({path: 'calc-' + box.getAttribute('data-calc'), event: true}); } catch (x) {} };
    f.addEventListener('submit', run);
    f.addEventListener('change', function () { if (out.innerHTML) run(); });
  });
})();
