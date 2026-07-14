const fs=require('fs'), vm=require('vm'), {webcrypto}=require('crypto');
const code=fs.readFileSync('expansion-calculators.js','utf8');
function run(kind, values){
  const elements={resultLabel:{},resultValue:{},resultDetails:{replaceChildren(){}},calcResult:{classList:{add(){},remove(){}}},themeToggle:null,hamburgerBtn:null,navLinks:null};
  for(const [id,value] of Object.entries(values)) elements[id]={value:String(value),checked:value===true};
  const document={body:{dataset:{calculator:kind},classList:{add(){},toggle(){},contains(){return false}}},getElementById:id=>elements[id]||null,querySelectorAll:()=>[],createElement:()=>({textContent:''})};
  const context={document,window:{alert:m=>{throw new Error(m)}},localStorage:{getItem(){return null},setItem(){}},crypto:webcrypto,TextEncoder,TextDecoder,Uint8Array,Map,Math,Number,Intl,Array,String,console,btoa:s=>Buffer.from(s,'binary').toString('base64'),atob:s=>Buffer.from(s,'base64').toString('binary')};
  vm.createContext(context); vm.runInContext(code,context); context.window.calculate();
  if(!elements.resultValue.textContent) throw new Error(kind+' produced no result');
  return elements.resultValue.textContent;
}
const cases={
 concrete:{length:20,width:10,depth:4,waste:10},roofing:{length:40,width:25,pitch:6,waste:10},paint:{perimeter:60,height:8,openings:60,coats:2,coverage:350},flooring:{length:15,width:12,waste:10},gravel:{length:30,width:10,depth:4,density:1.4},
 gpa:{grades:'4,3',credits:'3,3'},grade:{earned:87,possible:100},median:{values:'4,7,7,9,13'},stddev:{values:'2,4,4,4,5,5,7,9',method:'population'},regression:{xvalues:'1,2,3',yvalues:'2,4,6'},
 'auto-loan':{price:30000,down:5000,trade:0,tax:6,rate:7,months:60},amortization:{principal:250000,rate:6.5,years:30},retirement:{current:50000,monthly:500,return:6,years:25,inflation:2.5},debt:{balance:12000,rate:18,payment:400},inflation:{amount:100,rate:3,years:10},vat:{amount:100,rate:20,direction:'add'},'credit-card':{balance:5000,rate:22,payment:200},
 density:{mass:10,volume:2},ohms:{voltage:12,current:2,resistance:''},'voltage-drop':{current:10,resistance:.005,length:20},power:{voltage:230,current:5,factor:1},
 subnet:{ip:'192.168.1.42',prefix:24},password:{length:20,symbols:true},base64:{text:'Hello',direction:'encode'},url:{text:'hello world',direction:'encode'},
 volume:{value:1,from:'gal',to:'l'},pressure:{value:1,from:'atm',to:'pa'},energy:{value:1,from:'kwh',to:'j'},'power-converter':{value:1,from:'hp',to:'w'},angle:{value:180,from:'deg',to:'rad'},
 salary:{gross:60000,incomeTax:15,payrollTax:7.5,deductions:0,currency:'$'}
};
const observed={}; for(const [kind,values] of Object.entries(cases)) observed[kind]=run(kind,values);
if(!observed.concrete.includes('2.716')) throw new Error('Concrete volume regression: '+observed.concrete);
if(!observed.ohms.includes('6')) throw new Error('Ohm law regression: '+observed.ohms);
if(!observed.subnet.includes('255.255.255.0')) throw new Error('Subnet mask regression: '+observed.subnet);
if(!observed.base64.includes('SGVsbG8=')) throw new Error('Base64 regression: '+observed.base64);
console.log('PASS: '+Object.keys(cases).length+' calculator engines exercised.');
