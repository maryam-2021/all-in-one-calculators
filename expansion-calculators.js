(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const n = id => {
    const value = $(id)?.value;
    return value == null || String(value).trim() === '' ? NaN : Number(value);
  };
  const s = id => String($(id)?.value || '').trim();
  const nums = id => s(id).split(/[\s,;]+/).filter(Boolean).map(Number);
  const money = value => new Intl.NumberFormat(undefined, {maximumFractionDigits: 2}).format(value);
  const fixed = (value, digits = 2) => Number(value).toLocaleString(undefined, {maximumFractionDigits: digits});
  const invalid = message => { window.alert(message || 'Please enter valid values.'); return null; };
  function result(label, value, details) {
    $('resultLabel').textContent = label;
    $('resultValue').textContent = value;
    $('resultDetails').replaceChildren(...details.map(text => {
      const span = document.createElement('span'); span.textContent = text; return span;
    }));
    $('calcResult').classList.add('visible');
  }
  function payment(principal, annualRate, months) {
    if (months <= 0) return NaN;
    const r = annualRate / 1200;
    return r === 0 ? principal / months : principal * r / (1 - Math.pow(1 + r, -months));
  }
  function compoundMonths(balance, annualRate, monthlyPayment) {
    const r = annualRate / 1200; let months = 0, interest = 0;
    while (balance > 0.005 && months < 1200) {
      const charge = balance * r;
      if (monthlyPayment <= charge) return null;
      interest += charge; balance = Math.max(0, balance + charge - monthlyPayment); months++;
    }
    return {months, interest};
  }
  function convert(value, from, to, factors) { return value * factors[from] / factors[to]; }
  function calculate() {
    const kind = document.body.dataset.calculator;
    let a, b, c, d, x, y, out;
    if (kind === 'concrete') {
      a=n('length'); b=n('width'); c=n('depth'); d=n('waste'); if(!(a>0&&b>0&&c>0&&d>=0)) return invalid();
      x=a*b*(c/12)*(1+d/100); y=x/27; return result('Concrete required', fixed(y,3)+' yd³', [fixed(x,2)+' ft³ including waste', Math.ceil(x/0.6)+' estimated 80 lb bags']);
    }
    if (kind === 'roofing') {
      a=n('length'); b=n('width'); c=n('pitch'); d=n('waste'); if(!(a>0&&b>0&&c>=0&&d>=0)) return invalid();
      x=a*b*Math.sqrt(1+Math.pow(c/12,2))*(1+d/100); return result('Estimated roof area', fixed(x)+' ft²', [fixed(x/100,2)+' roofing squares', 'Includes '+fixed(d,1)+'% waste']);
    }
    if (kind === 'paint') {
      a=n('perimeter'); b=n('height'); c=n('openings'); d=n('coats'); x=n('coverage'); if(!(a>0&&b>0&&c>=0&&d>0&&x>0)) return invalid();
      y=Math.max(0,a*b-c)*d/x; return result('Paint required', fixed(y,2)+' gallons', [fixed(Math.max(0,a*b-c))+' ft² paintable area', Math.ceil(y)+' whole gallons to purchase']);
    }
    if (kind === 'flooring') {
      a=n('length'); b=n('width'); c=n('waste'); if(!(a>0&&b>0&&c>=0)) return invalid(); x=a*b*(1+c/100);
      return result('Flooring required', fixed(x)+' ft²', [fixed(a*b)+' ft² room area', 'Includes '+fixed(c,1)+'% waste']);
    }
    if (kind === 'gravel') {
      a=n('length'); b=n('width'); c=n('depth'); d=n('density'); if(!(a>0&&b>0&&c>0&&d>0)) return invalid(); x=a*b*(c/12)/27; y=x*d;
      return result('Gravel required', fixed(x,2)+' yd³', [fixed(y,2)+' tons at the selected density', fixed(x*27,1)+' ft³']);
    }
    if (kind === 'gpa') {
      x=nums('grades'); y=nums('credits'); if(!x.length||x.length!==y.length||x.some(v=>v<0||v>4)||y.some(v=>v<=0)) return invalid('Enter the same number of grade points and credits.');
      a=y.reduce((p,v)=>p+v,0); b=x.reduce((p,v,i)=>p+v*y[i],0); return result('Weighted GPA', fixed(b/a,3), [fixed(b,2)+' quality points', fixed(a,2)+' total credits']);
    }
    if (kind === 'grade') {
      a=n('earned'); b=n('possible'); if(!(a>=0&&b>0)) return invalid(); x=a/b*100;
      return result('Course grade', fixed(x,2)+'%', [fixed(a,2)+' of '+fixed(b,2)+' points', x>=90?'Typical letter grade: A':x>=80?'Typical letter grade: B':x>=70?'Typical letter grade: C':x>=60?'Typical letter grade: D':'Typical letter grade: F']);
    }
    if (kind === 'median') {
      x=nums('values'); if(!x.length||x.some(v=>!Number.isFinite(v))) return invalid(); x.sort((p,q)=>p-q); a=x.reduce((p,v)=>p+v,0)/x.length; b=x.length%2?x[(x.length-1)/2]:(x[x.length/2-1]+x[x.length/2])/2;
      const counts=new Map(); x.forEach(v=>counts.set(v,(counts.get(v)||0)+1)); c=Math.max(...counts.values()); d=[...counts].filter(v=>v[1]===c&&c>1).map(v=>v[0]).join(', ')||'No mode';
      return result('Summary statistics','Mean '+fixed(a,3),['Median: '+fixed(b,3),'Mode: '+d,'Count: '+x.length]);
    }
    if (kind === 'stddev') {
      x=nums('values'); b=s('method'); if(x.length<(b==='sample'?2:1)||x.some(v=>!Number.isFinite(v))) return invalid(); a=x.reduce((p,v)=>p+v,0)/x.length; c=x.reduce((p,v)=>p+Math.pow(v-a,2),0)/(x.length-(b==='sample'?1:0));
      return result('Standard deviation',fixed(Math.sqrt(c),5),['Mean: '+fixed(a,5),'Variance: '+fixed(c,5),b==='sample'?'Sample (n - 1)':'Population (n)']);
    }
    if (kind === 'regression') {
      x=nums('xvalues'); y=nums('yvalues'); if(x.length<2||x.length!==y.length||x.some(v=>!Number.isFinite(v))||y.some(v=>!Number.isFinite(v))) return invalid('Enter matching X and Y lists with at least two points.');
      a=x.reduce((p,v)=>p+v,0)/x.length; b=y.reduce((p,v)=>p+v,0)/y.length; c=x.reduce((p,v,i)=>p+(v-a)*(y[i]-b),0)/x.reduce((p,v)=>p+Math.pow(v-a,2),0); d=b-c*a;
      const ssTot=y.reduce((p,v)=>p+Math.pow(v-b,2),0), ssRes=y.reduce((p,v,i)=>p+Math.pow(v-(c*x[i]+d),2),0); return result('Best-fit line','y = '+fixed(c,5)+'x + '+fixed(d,5),['Slope: '+fixed(c,5),'Intercept: '+fixed(d,5),'R²: '+fixed(ssTot?1-ssRes/ssTot:1,5)]);
    }
    if (kind === 'auto-loan') {
      a=n('price'); b=n('down'); c=n('trade'); d=n('tax'); x=n('rate'); y=n('months'); if(!(a>0&&b>=0&&c>=0&&d>=0&&x>=0&&y>0)) return invalid(); const principal=(a-c)*(1+d/100)-b, p=payment(principal,x,y); if(!(principal>0)) return invalid('Financed amount must be positive.');
      return result('Estimated monthly payment','$'+money(p),['Amount financed: $'+money(principal),'Total interest: $'+money(p*y-principal),'Total of payments: $'+money(p*y)]);
    }
    if (kind === 'amortization') {
      a=n('principal'); b=n('rate'); c=n('years'); if(!(a>0&&b>=0&&c>0)) return invalid(); d=Math.round(c*12); x=payment(a,b,d);
      return result('Monthly payment','$'+money(x),['Total interest: $'+money(x*d-a),'Total paid: $'+money(x*d),d+' monthly payments']);
    }
    if (kind === 'retirement') {
      a=n('current'); b=n('monthly'); c=n('return'); d=n('years'); x=n('inflation'); if(!(a>=0&&b>=0&&c>=0&&d>0&&x>=0)) return invalid(); const r=c/1200,m=Math.round(d*12),future=a*Math.pow(1+r,m)+(r?b*(Math.pow(1+r,m)-1)/r:b*m),real=future/Math.pow(1+x/100,d);
      return result('Projected savings','$'+money(future),['In today’s money: $'+money(real),'Total contributions: $'+money(a+b*m),'Assumes constant returns and monthly deposits']);
    }
    if (kind === 'debt' || kind === 'credit-card') {
      a=n('balance'); b=n('rate'); c=n('payment'); if(!(a>0&&b>=0&&c>0)) return invalid(); x=compoundMonths(a,b,c); if(!x) return invalid('Payment must be higher than monthly interest.');
      return result('Estimated payoff time',Math.floor(x.months/12)+' yr '+(x.months%12)+' mo',['Total interest: $'+money(x.interest),'Total paid: $'+money(a+x.interest),x.months+' monthly payments']);
    }
    if (kind === 'inflation') {
      a=n('amount'); b=n('rate'); c=n('years'); if(!(a>=0&&b>-100&&c>=0)) return invalid(); x=a*Math.pow(1+b/100,c);
      return result('Future equivalent','$'+money(x),['Price increase: $'+money(x-a),'Purchasing-power factor: '+fixed(Math.pow(1+b/100,c),4)]);
    }
    if (kind === 'vat') {
      a=n('amount'); b=n('rate'); c=s('direction'); if(!(a>=0&&b>=0)) return invalid(); x=c==='add'?a*(1+b/100):a/(1+b/100); y=c==='add'?x-a:a-x;
      return result(c==='add'?'Gross total':'Net amount','$'+money(x),['VAT: $'+money(y),'Rate: '+fixed(b,2)+'%']);
    }
    if (kind === 'density') {
      a=n('mass'); b=n('volume'); if(!(a>=0&&b>0)) return invalid(); return result('Density',fixed(a/b,5)+' kg/m³',['Mass: '+fixed(a)+' kg','Volume: '+fixed(b)+' m³']);
    }
    if (kind === 'ohms') {
      a=n('voltage'); b=n('current'); c=n('resistance'); const count=[a,b,c].filter(Number.isFinite).length; if(count!==2) return invalid('Enter exactly two values and leave the unknown blank.');
      if(!Number.isFinite(a)) return result('Voltage',fixed(b*c,5)+' V',['V = I × R']); if(!Number.isFinite(b)) return result('Current',fixed(a/c,5)+' A',['I = V ÷ R']); return result('Resistance',fixed(a/b,5)+' Ω',['R = V ÷ I']);
    }
    if (kind === 'voltage-drop') {
      a=n('current'); b=n('resistance'); c=n('length'); if(!(a>=0&&b>=0&&c>=0)) return invalid(); x=a*b*c*2; return result('Voltage drop',fixed(x,4)+' V',['Round-trip conductor length: '+fixed(c*2)+' m','Uses entered resistance per metre','Verify conductor and code requirements locally']);
    }
    if (kind === 'power') {
      a=n('voltage'); b=n('current'); c=n('factor'); if(!(a>=0&&b>=0&&c>=0&&c<=1)) return invalid(); x=a*b*c; return result('Electrical power',fixed(x,3)+' W',[fixed(x/1000,5)+' kW','P = V × I × power factor']);
    }
    if (kind === 'subnet') {
      const parts=s('ip').split('.').map(Number), prefix=n('prefix'); if(parts.length!==4||parts.some(v=>!Number.isInteger(v)||v<0||v>255)||!Number.isInteger(prefix)||prefix<0||prefix>32) return invalid('Enter a valid IPv4 address and CIDR prefix.');
      const ip=parts.reduce((v,p)=>(v*256+p)>>>0,0), mask=prefix===0?0:(0xffffffff << (32-prefix))>>>0, network=(ip&mask)>>>0, broadcast=(network|(~mask>>>0))>>>0, fmt=v=>[24,16,8,0].map(sh=>(v>>>sh)&255).join('.'), hosts=prefix>=31?0:Math.pow(2,32-prefix)-2;
      return result('Network '+fmt(network)+'/'+prefix,'Mask '+fmt(mask),['Broadcast: '+fmt(broadcast),'Usable hosts: '+hosts.toLocaleString(),'Address count: '+Math.pow(2,32-prefix).toLocaleString()]);
    }
    if (kind === 'password') {
      a=n('length'); if(!Number.isInteger(a)||a<8||a>128) return invalid('Choose a length from 8 to 128.'); let chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'; if($('symbols').checked) chars+='!@#$%^&*()-_=+'; const random=new Uint32Array(a); crypto.getRandomValues(random); x=Array.from(random,v=>chars[v%chars.length]).join(''); return result('Generated password',x,['Length: '+a+' characters',$('symbols').checked?'Includes symbols':'Letters and numbers only','Generated locally with Web Crypto']);
    }
    if (kind === 'base64') {
      a=s('text'); b=s('direction'); try { x=b==='encode'?btoa(String.fromCharCode(...new TextEncoder().encode(a))):new TextDecoder().decode(Uint8Array.from(atob(a),ch=>ch.charCodeAt(0))); } catch(e){ return invalid('The input is not valid for that operation.'); } return result(b==='encode'?'Base64 output':'Decoded text',x,['Processed locally in your browser']);
    }
    if (kind === 'url') {
      a=s('text'); b=s('direction'); try{x=b==='encode'?encodeURIComponent(a):decodeURIComponent(a);}catch(e){return invalid('The input contains invalid URL encoding.');} return result(b==='encode'?'Encoded component':'Decoded component',x,['Uses JavaScript URI-component rules']);
    }
    if (['volume','pressure','energy','power-converter','angle'].includes(kind)) {
      const factors={volume:{l:1,ml:.001,m3:1000,gal:3.785411784,ft3:28.316846592},pressure:{pa:1,kpa:1000,bar:100000,psi:6894.757293,atm:101325},energy:{j:1,kj:1000,kwh:3600000,cal:4.184,btu:1055.055853},'power-converter':{w:1,kw:1000,hp:745.699872,btuhr:.29307107},angle:{deg:1,rad:180/Math.PI,grad:.9,turn:360}}[kind]; a=n('value'); b=s('from'); c=s('to'); if(!Number.isFinite(a)||!factors[b]||!factors[c]) return invalid(); x=convert(a,b,c,factors); return result('Converted value',fixed(x,8)+' '+c.toUpperCase(),[fixed(a,8)+' '+b.toUpperCase()+' = '+fixed(x,8)+' '+c.toUpperCase()]);
    }
    if (kind === 'salary') {
      a=n('gross'); b=n('incomeTax'); c=n('payrollTax'); d=n('deductions'); if(!(a>=0&&b>=0&&c>=0&&d>=0)) return invalid(); x=Math.max(0,a-a*b/100-a*c/100-d);
      return result('Estimated annual take-home',s('currency')+money(x),['Monthly take-home: '+s('currency')+money(x/12),'Income tax estimate: '+s('currency')+money(a*b/100),'Payroll/social estimate: '+s('currency')+money(a*c/100),'Other deductions: '+s('currency')+money(d)]);
    }
  }
  window.calculate = calculate;
  window.resetCalc = function () { document.querySelectorAll('.calc-form input, .calc-form textarea').forEach(el => { if(el.type!=='checkbox') el.value=''; }); $('calcResult').classList.remove('visible'); };
  document.querySelectorAll('.faq-question').forEach(button => button.addEventListener('click', () => button.closest('.faq-item').classList.toggle('open')));
  const theme=$('themeToggle'); if(theme){ if(localStorage.getItem('theme')==='light') document.body.classList.add('light-mode'); theme.addEventListener('click',()=>{document.body.classList.toggle('light-mode');localStorage.setItem('theme',document.body.classList.contains('light-mode')?'light':'dark');}); }
  const menu=$('hamburgerBtn'), nav=$('navLinks'); if(menu&&nav) menu.addEventListener('click',()=>nav.classList.toggle('active'));
}());
