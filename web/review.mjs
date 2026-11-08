export const presets = [
  {name:'继任与估值', query:'business succession SME valuation', boolean:'("business succession" OR "external succession" OR Unternehmensnachfolge) AND (valuation OR "firm value" OR Unternehmensbewertung OR Kaufpreis) AND (SME OR SMEs OR KMU OR Mittelstand)'},
  {name:'德国中小企业', query:'Germany Mittelstand SME business succession', boolean:'(Germany OR German OR Deutschland) AND (SME OR SMEs OR Mittelstand OR KMU) AND ("business succession" OR "external succession" OR Unternehmensnachfolge OR Nachfolgermangel)'},
  {name:'企业主依赖', query:'owner dependence personal goodwill business valuation', boolean:'("owner dependence" OR "founder dependence" OR "key person risk" OR "personal goodwill" OR Inhaberabhängigkeit) AND (valuation OR acquisition OR Unternehmensbewertung)'},
  {name:'退休与成交价格', query:'owner retirement business acquisition transaction price', boolean:'("owner retirement" OR "founder exit" OR "external succession") AND ("transaction price" OR "acquisition price" OR "bargaining power" OR Kaufpreis)'},
  {name:'交接与知识转移', query:'SME business succession knowledge transfer', boolean:'("business succession" OR acquisition) AND ("knowledge transfer" OR "human capital" OR "customer retention") AND (SME OR "family business")'},
  {name:'德文关键词', query:'KMU Mittelstand Nachfolgermangel Unternehmensbewertung', boolean:'(KMU OR Mittelstand OR Familienunternehmen) AND (Nachfolgermangel OR "fehlende Nachfolge" OR "ungelöste Unternehmensnachfolge") AND (Unternehmensbewertung OR Unternehmenswert OR Kaufpreis OR Unternehmensverkauf)'}
];
export function key(item) {return item.doi ? item.doi.toLowerCase() : `${item.title}|${item.journal}`;}
export function csv(items) {
  const fields=['title','authors','year','journal','doi','url','abstract','notes'];
  const cell=value=>'"'+String(value??'').replace(/^[\s]*[=+@-]/,'\'$&').replaceAll('"','""')+'"';
  return '\uFEFF'+[fields,...items.map(i=>fields.map(f=>i[f]??''))].map(row=>row.map(cell).join(',')).join('\r\n');
}
export function ris(items) {
  const clean=v=>String(v??'').replace(/[\r\n]+/g,' ');
  return items.map(i=>[['TY','JOUR'],['TI',i.title],['JO',i.journal],['PY',i.year],['DO',i.doi],['UR',i.url],['AB',i.abstract],['N1',i.notes],['N1',i.authors?'Authors: '+i.authors:'']].filter(([,v])=>v).map(([k,v])=>`${k}  - ${clean(v)}`).join('\n')+'\nER  -\n').join('\n');
}
