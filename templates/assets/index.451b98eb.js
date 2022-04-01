var me=Object.defineProperty;var ge=(t,e,s)=>e in t?me(t,e,{enumerable:!0,configurable:!0,writable:!0,value:s}):t[e]=s;var U=(t,e,s)=>(ge(t,typeof e!="symbol"?e+"":e,s),s);import{c as w,r as W,o as f,a as Z,m as L,d as Y,b as S,e as O,f as R,w as r,g as c,h as g,i as k,t as D,u as i,_ as j,j as T,M as ee,k as N,l as C,n as M,F as E,p as q,q as he,P as te,B as H,I as ve,s as we,U as ye,v as G,x as be,y as se,S as ke,z as xe,A as V,C as oe,D as ne,E as Se,G as De,L as $e,H as Le,J as Ce,K as Ue,N as Me,O as Oe,Q as Ie,R as ae,T as re,V as Fe,W as Ae,X as Ne,Y as Pe,Z as Re,$ as Te,a0 as qe,a1 as He,a2 as je,a3 as Ee,a4 as Be,a5 as Ke,a6 as ze,a7 as We,a8 as Ve,a9 as Qe,aa as Je}from"./vendor.3e83eb86.js";const Ze=function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const a of document.querySelectorAll('link[rel="modulepreload"]'))o(a);new MutationObserver(a=>{for(const l of a)if(l.type==="childList")for(const m of l.addedNodes)m.tagName==="LINK"&&m.rel==="modulepreload"&&o(m)}).observe(document,{childList:!0,subtree:!0});function s(a){const l={};return a.integrity&&(l.integrity=a.integrity),a.referrerpolicy&&(l.referrerPolicy=a.referrerpolicy),a.crossorigin==="use-credentials"?l.credentials="include":a.crossorigin==="anonymous"?l.credentials="omit":l.credentials="same-origin",l}function o(a){if(a.ep)return;a.ep=!0;const l=s(a);fetch(a.href,l)}};Ze();var I=(t,e)=>{const s=t.__vccOpts||t;for(const[o,a]of e)s[o]=a;return s};const Ge={};function Xe(t,e){const s=W("router-view");return f(),w(s)}var Ye=I(Ge,[["render",Xe]]);const et={Accept:"application/json","Content-Type":"application/json;charset=UTF-8","Access-Control-Allow-Origin":"*"},tt=t=>{const e=localStorage.getItem("accessToken");if(e!=null){if(t.headers===void 0)return t;t.headers.Authorization=`Bearer ${e}`}return t};class st{constructor(){U(this,"instance",null)}get http(){return this.instance!=null?this.instance:this.initHttp()}initHttp(){const e=Z.create({baseURL:"",headers:et});return e.interceptors.request.use(tt,s=>Promise.reject(s)),e.interceptors.response.use(s=>{if(s.headers&&s.headers.authorization){const o=s.headers.authorization.split(" ")[1];localStorage.setItem("accessToken",o)}return s},s=>{const{response:o}=s;return this.handleError(o)}),this.instance=e,e}request(e){return this.http.request(e)}get(e,s){return this.http.get(e,s)}post(e,s,o){return this.http.post(e,s,o)}put(e,s,o){return this.http.put(e,s,o)}delete(e,s){return this.http.delete(e,s)}handleError(e){const{status:s}=e;switch(console.error("response status= "+s),Z.isAxiosError(e)?console.error("is axios error "+e):console.error("no axios error"+e),s){case 500:{L.error(`Internal server error(${s})`);break}case 403:{L.error(`Forbidden(${s})`);break}case 401:{L.error(`Unauthorized(${s})`);break}case 404:{L.error(`Not found(${s})`);break}case 429:{L.error(`Too many requests error(${s})`);break}default:L.error(`Unknown error(${s})`);break}return Promise.reject(e)}}const B=new st,ot=[{title:"COM Number",key:"name",dataIndex:"name",filters:[],onFilter:(t,e)=>e.name.indexOf(t)===0,sorter:(t,e)=>t.name.length-e.name.length,sortDirections:["descend","ascend"]},{title:"MAC Address",key:"mac",dataIndex:"mac",sortDirections:["descend","ascend"],sorter:(t,e)=>t.mac.length-e.mac.length},{title:"Label",key:"label",dataIndex:"label",filters:[],filterMultiple:!1,onFilter:(t,e)=>e.label.indexOf(t)===0,sorter:(t,e)=>t.label.length-e.label.length,sortDirections:["descend","ascend"]},{title:"SW Version",key:"swversion",dataIndex:"swversion",filters:[],filterMultiple:!1,onFilter:(t,e)=>e.swversion.indexOf(t)===0,sorter:(t,e)=>t.swversion.length-e.swversion.length,sortDirections:["descend","ascend"]},{title:"Configured Status",key:"configured",dataIndex:"configured",slots:{customRender:"configured"},filters:[],filterMultiple:!1,sortDirections:["descend","ascend"]},{title:"Connected",key:"connected",dataIndex:"connected",slots:{customRender:"connected"},filters:[],filterMultiple:!1,sortDirections:["descend","ascend"]},{title:"Working mode",key:"state",dataIndex:"state",slots:{customRender:"state"},filters:[],filterMultiple:!1,sorter:(t,e)=>t.state-e.state,sortDirections:["descend","ascend"]},{title:"Identify",key:"identify",dataIndex:"identify",slots:{customRender:"identify"}}],K=t=>{let e="Unknown";switch(t){case 1:e="Normal";break;case 2:e="Bootloader";break;case 3:e="Upgrade";break}return e},ce=[{title:"COM Number",key:"name",dataIndex:"name",filters:[],onFilter:(t,e)=>e.name.indexOf(t)===0,sorter:(t,e)=>t.name.length-e.name.length,sortDirections:["descend","ascend"]},{title:"MAC Address",key:"mac",dataIndex:"mac",sortDirections:["descend","ascend"],sorter:(t,e)=>t.mac.length-e.mac.length},{title:"Label",key:"label",dataIndex:"label",filters:[],filterMultiple:!1,onFilter:(t,e)=>e.label.indexOf(t)===0,sorter:(t,e)=>t.label.length-e.label.length,sortDirections:["descend","ascend"]},{title:"SW Version",key:"swversion",dataIndex:"swversion",filters:[],filterMultiple:!1,onFilter:(t,e)=>e.swversion.indexOf(t)===0,sorter:(t,e)=>t.swversion.length-e.swversion.length,sortDirections:["descend","ascend"]},{title:"Configured Status",key:"configured",dataIndex:"configured",slots:{customRender:"configured"},filters:[],filterMultiple:!1,sortDirections:["descend","ascend"]},{title:"Connected",key:"connected",dataIndex:"connected",slots:{customRender:"connected"},filters:[],filterMultiple:!1,sortDirections:["descend","ascend"]},{title:"Working mode",key:"state",dataIndex:"state",slots:{customRender:"state"},filters:[],filterMultiple:!1,sorter:(t,e)=>t.state-e.state,sortDirections:["descend","ascend"]}],nt=[{title:"COM Number",key:"name",dataIndex:"name",filters:[],onFilter:(t,e)=>e.name.indexOf(t)===0,sorter:(t,e)=>t.name.length-e.name.length,sortDirections:["descend","ascend"]},{title:"MAC Address",key:"mac",dataIndex:"mac",sortDirections:["descend","ascend"],sorter:(t,e)=>t.mac.length-e.mac.length},{title:"Label",key:"label",dataIndex:"label",filters:[],filterMultiple:!1,onFilter:(t,e)=>e.label.indexOf(t)===0,sorter:(t,e)=>t.label.length-e.label.length,sortDirections:["descend","ascend"]},{title:"SW Version",key:"swversion",dataIndex:"swversion",filters:[],filterMultiple:!1,onFilter:(t,e)=>e.swversion.indexOf(t)===0,sorter:(t,e)=>t.swversion.length-e.swversion.length,sortDirections:["descend","ascend"]},{title:"Configured Status",key:"configured",dataIndex:"configured",slots:{customRender:"configured"},filters:[],filterMultiple:!1,sortDirections:["descend","ascend"]},{title:"Connected",key:"connected",dataIndex:"connected",slots:{customRender:"connected"},filters:[],filterMultiple:!1,sortDirections:["descend","ascend"]},{title:"Working mode",key:"state",dataIndex:"state",slots:{customRender:"state"},filters:[],filterMultiple:!1,sorter:(t,e)=>t.state-e.state,sortDirections:["descend","ascend"]},{title:"Progress",key:"progress",dataIndex:"progress",slots:{customRender:"progress"}}],Q=async()=>{const t=[];try{(await B.get("/api/1/devices")).data.data.forEach(function(s){t.push({key:s.mac,name:s.name+`

`+s.ip,ip:s.ip,mac:s.mac,label:s.label,swversion:s.swversion,hwversion:s.hwversion,configured:s.configured,connected:s.connected,state:s.state,identify:s.mac,isSelect:!1,progress:0})})}catch(e){console.error("fetchDevices error= "+e)}return t},at=async t=>{try{return(await B.put(`/api/1/devices/${t}`,{command:"identify"})).data}catch(e){return console.error("identifyDevice error= "+e),null}},F=Y("devices",{state:()=>({deviceList:[],upgradeMac:[],selectFirmware:""}),persist:{enabled:!0,strategies:[{key:"devices",storage:localStorage,paths:["deviceList"]}]},getters:{allDevices(t){return t.deviceList},selectedDevices(t){return t.deviceList.filter(e=>e.isSelect)},getUpgradeMac(t){return t.upgradeMac},selectedFirmware(t){return t.selectFirmware}},actions:{addUpgradeMac(t){this.upgradeMac=t},deleteUpgradeMac(){this.upgradeMac=[]},addSelectFirmware(t){this.selectFirmware=t},deleteSelectFirmware(){this.selectFirmware=""},addDevice(t){!t||this.deviceList.push(t)},addDevices(t){if(t.length===0)return;const e=this.deviceList.length===0;for(let s=0;s<t.length;s++)this.deviceList.find(a=>a.mac==t[s].mac)||this.deviceList.push(t[s]);if(!e)for(let s=0;s<this.deviceList.length;s++){const o=t.find(a=>a.mac===this.deviceList[s].mac);o?(this.deviceList[s].configured=o.configured,this.deviceList[s].connected=o.connected,this.deviceList[s].hwversion=o.hwversion,this.deviceList[s].key=o.key,this.deviceList[s].label=o.label,this.deviceList[s].mac=o.mac,this.deviceList[s].name=o.name,this.deviceList[s].ip=o.ip,this.deviceList[s].state=o.state,this.deviceList[s].swversion=o.swversion):this.deviceList.splice(s,1)}},updateSelectDevices(t){if(t.length===0){this.deviceList.forEach(e=>{e.isSelect=!1});return}for(let e=0;e<this.deviceList.length;e++){const s=this.deviceList[e].mac;for(let o=0;o<t.length;o++)if(s===t[o]){this.deviceList[e].isSelect=!0;break}else o===t.length-1&&(this.deviceList[e].isSelect=!1)}},updateDevice(t){for(let e=0;e<this.deviceList.length;e++)this.deviceList[e].mac===t.mac&&(this.deviceList[e].configured=t.configured,this.deviceList[e].connected=t.connected,this.deviceList[e].hwversion=t.hwversion,this.deviceList[e].state=t.state,this.deviceList[e].swversion=t.swversion)},resetAllDeviceProgress(){for(let t=0;t<this.deviceList.length;t++)this.deviceList[t].progress=0},delete(t){!t||this.deviceList.forEach((e,s)=>{e.mac===t.mac&&this.deviceList.splice(s,1)})},deleteAllDevice(){this.deviceList=[]}}});const ie=S({emits:["selectDevices"],setup(t,{expose:e,emit:s}){const o=O({selectedRowKeys:[],loading:!1,visible:!1}),a=F(),l=d=>{console.log("selectedRowKeys changed: ",d),o.selectedRowKeys=d},m=()=>{a.updateSelectDevices(o.selectedRowKeys),s.call(this,"selectDevices"),o.visible=!1};return R(async()=>{o.loading=!0;const d=await Q();a.addDevices(d),a.selectedDevices.length>0&&a.selectedDevices.filter(p=>p.isSelect).forEach(p=>o.selectedRowKeys.push(p.mac)),o.loading=!1}),e({showOrHideModal:d=>{o.visible=d}}),(d,p)=>{const n=j,u=T,y=ee;return f(),w(y,{visible:i(o).visible,"onUpdate:visible":p[0]||(p[0]=_=>i(o).visible=_),title:"Select Device",width:"100%","wrap-class-name":"full-modal",onOk:m},{default:r(()=>[c(u,{columns:i(ce),"data-source":i(a).deviceList,"row-selection":{selectedRowKeys:i(o).selectedRowKeys,onChange:l},loading:i(o).loading,bordered:""},{configured:r(({text:_})=>[g("span",null,[(f(),w(n,{key:_,color:_?"green":"volcano"},{default:r(()=>[k(D(_?"Configured":"No Configure"),1)]),_:2},1032,["color"]))])]),connected:r(({text:_})=>[g("span",null,[(f(),w(n,{key:_,color:_?"green":"volcano"},{default:r(()=>[k(D(_?"Online":"Offline"),1)]),_:2},1032,["color"]))])]),state:r(({text:_})=>[g("span",null,[(f(),w(n,{key:_,color:_===1?"green":_==0?"volcano":"geekblue"},{default:r(()=>[k(D(i(K)(_)),1)]),_:2},1032,["color"]))])]),_:1},8,["columns","data-source","row-selection","loading"])]),_:1},8,["visible"])}}});function le(t,e){t!==null&&(t.code===0&&e?L.success(e):L.error(t.message))}const rt=g("span",null," Please add device ",-1),ct=k("Add Now"),it=k(" Identify "),lt=S({setup(t){const e=O({loading:!1}),s=F(),o=N(),a=(n,u,y)=>{console.log("params",n,u,y)};let l=N(new Map);const m=async n=>{l.value.set(n,!0);const u=await at(n);le(u,`Identify device [mac=${n}] success!`),(u==null?void 0:u.code)===0?setTimeout(()=>{l.value.set(n,!1)},5e3):l.value.set(n,!1)},h=()=>{var n;(n=o.value)==null||n.showOrHideModal(!0)},d=()=>{var n;(n=o.value)==null||n.showOrHideModal(!0)},p=()=>{};return R(async()=>{e.loading=!0;const n=await Q();s.addDevices(n),e.loading=!1}),(n,u)=>{const y=H,_=q,x=he,$=j,v=T;return f(),C(E,null,[i(s).selectedDevices.length!==0?(f(),w(_,{key:0,justify:"end",style:{margin:"16px 16px 16px 16px"}},{default:r(()=>[c(y,{type:"primary",onClick:d,style:{width:"60px"}},{default:r(()=>[c(i(te))]),_:1})]),_:1})):M("",!0),i(s).selectedDevices.length===0?(f(),w(x,{key:1,image:"https://gw.alipayobjects.com/mdn/miniapp_social/afts/img/A*pevERLJC9v0AAAAAAAAAAABjAQAAAQ/original","image-style":{height:"100px"},style:{margin:"100px 0 0 0 "}},{description:r(()=>[rt]),default:r(()=>[c(y,{type:"primary",shape:"round",style:{margin:"30px 0 0 0"},onClick:h},{default:r(()=>[ct]),_:1})]),_:1})):M("",!0),i(s).selectedDevices.length!==0?(f(),w(v,{key:2,columns:i(ot),"data-source":i(s).selectedDevices,loading:i(e).loading,bordered:"",style:{margin:"0 10px 0 0"},onChange:a},{name:r(({text:b})=>[g("div",null,D(b),1)]),configured:r(({text:b})=>[g("span",null,[(f(),w($,{key:b,color:b?"green":"volcano"},{default:r(()=>[k(D(b?"Configured":"No Configure"),1)]),_:2},1032,["color"]))])]),connected:r(({text:b})=>[g("span",null,[(f(),w($,{key:b,color:b?"green":"volcano"},{default:r(()=>[k(D(b?"Online":"Offline"),1)]),_:2},1032,["color"]))])]),state:r(({text:b})=>[g("span",null,[(f(),w($,{key:b,color:b===1?"green":b===0?"volcano":"geekblue"},{default:r(()=>[k(D(i(K)(b)),1)]),_:2},1032,["color"]))])]),identify:r(({text:b})=>[g("span",null,[c(y,{key:"identify",type:"primary",shape:"round",loading:i(l).get(b),onClick:A=>m(b)},{default:r(()=>[it]),_:2},1032,["loading","onClick"])])]),_:1},8,["columns","data-source","loading"])):M("",!0),c(ie,{ref_key:"showSelectModal",ref:o,onSelectDevices:p},null,512)],64)}}}),X=async()=>{const t=[];try{const e=await B.get("/api/1/firmwares");if(e.data.data.length===0)return t;e.data.data.forEach(function(s){t.push({key:s,name:s})})}catch(e){console.error("fetchFirmwares error= "+e)}return t},dt=async(t,e)=>{try{return(await B.put("/api/1/firmwares",{filename:t,devices:e})).data}catch(s){console.error("updateFirmware error= "+s)}return null},ut={class:"ant-upload-drag-icon"},pt=g("p",{class:"ant-upload-text"},"Click or drag file to this area to upload",-1),_t=g("p",{class:"ant-upload-hint"}," Support for a single or bulk upload. Strictly prohibit from uploading company data or other band files ",-1),ft=S({emits:["upload"],setup(t,{expose:e,emit:s}){const o=N([]);let a=N(!1);const l=h=>{const d=h.file.status;console.log("upload status "+d),d!=="uploading"&&console.log(h.file,h.fileList),d==="done"?(console.log("upload success"),s.call(this,"upload",!0)):d==="error"&&console.error("upload error")},m=h=>{a.value=h};return e({showOrHideModal:m}),(h,d)=>{const p=ye,n=ee;return f(),w(n,{visible:i(a),"onUpdate:visible":d[1]||(d[1]=u=>we(a)?a.value=u:a=u),title:"Select Firmware to upload",width:"40%",onOk:d[2]||(d[2]=u=>m(!1))},{default:r(()=>[c(p,{fileList:o.value,"onUpdate:fileList":d[0]||(d[0]=u=>o.value=u),name:"file",multiple:!0,action:"/api/1/firmwares",onChange:l},{default:r(()=>[g("p",ut,[c(i(ve))]),pt,_t]),_:1},8,["fileList"])]),_:1},8,["visible"])}}}),mt=S({emits:["selectedFirmware"],setup(t,{emit:e}){const s=[{title:"name",dataIndex:"name"}],o=O({selectedRowKeys:[],loading:!1,data:[]}),a=N(),l=()=>{var p;(p=a.value)==null||p.showOrHideModal(!0)},m=p=>{o.selectedRowKeys=p,e.call(this,"selectedFirmware",p[0]),d.addSelectFirmware(p[0])},h=async()=>{const p=await X();o.loading=!1,o.data=p},d=F();return R(async()=>{const p=await X();o.loading=!1,o.data=p,o.selectedRowKeys.push(d.selectFirmware)}),(p,n)=>{const u=H,y=q,_=T;return f(),C(E,null,[c(y,{justify:"end",style:{"margin-bottom":"16px"}},{default:r(()=>[c(u,{type:"primary",onClick:l,style:{width:"60px"}},{default:r(()=>[c(i(te))]),_:1})]),_:1}),c(_,{"row-selection":{selectedRowKeys:i(o).selectedRowKeys,type:"radio",onChange:m},columns:s,showHeader:!1,"data-source":i(o).data,loading:i(o).loading,pagination:{pageSize:8}},null,8,["row-selection","data-source","loading"]),c(ft,{ref_key:"showUploadFirmware",ref:a,onUpload:h},null,512)],64)}}}),z=Y("user",{state:()=>({user:{userName:"",password:""}}),persist:{enabled:!0,strategies:[{key:"currentUser",storage:localStorage}]},getters:{getUser(t){return t.user}},actions:{addUser(t){this.user=t},deleteUser(){this.user={userName:"",password:""}}}}),gt=S({emits:["selectDevices"],setup(t,{emit:e}){const s=O({selectedRowKeys:[],loading:!1,data:[],currentItem:"",ipList:[]}),o=F();z();const a=m=>{s.selectedRowKeys=m;const h=[];m.forEach(function(d){console.log("select device= "+d),h.push(d)}),e.call(this,"selectDevices",h)},l=m=>({disabled:m.state!==1||!m.connected});return R(async()=>{s.loading=!0;const m=await Q();s.loading=!1,s.data=m}),(m,h)=>{const d=j,p=T;return f(),w(p,{"row-selection":{selectedRowKeys:i(s).selectedRowKeys,getCheckboxProps:l,onChange:a},columns:i(ce),showHeader:!0,"data-source":i(o).selectedDevices,loading:i(s).loading,pagination:{pageSize:5}},{configured:r(({text:n})=>[g("span",null,[(f(),w(d,{key:n,color:n?"green":"volcano"},{default:r(()=>[k(D(n?"Configured":"No Configure"),1)]),_:2},1032,["color"]))])]),connected:r(({text:n})=>[g("span",null,[(f(),w(d,{key:n,color:n?"green":"volcano"},{default:r(()=>[k(D(n?"Online":"Offline"),1)]),_:2},1032,["color"]))])]),state:r(({text:n})=>[g("span",null,[(f(),w(d,{key:n,color:n===1?"green":n===0?"volcano":"geekblue"},{default:r(()=>[k(D(i(K)(n)),1)]),_:2},1032,["color"]))])]),_:1},8,["row-selection","columns","data-source","loading"])}}});class ht{constructor(){U(this,"subjects");this.subjects=new Map}$on(e,s){this.subjects.set(e,s),console.log("add topic= "+e)}$emit(e,s){console.log("topic= "+e+" size= "+this.subjects.values.length),this.subjects.forEach((o,a)=>{console.log("topic= "+e+" key= "+a),e.indexOf(a)!==-1&&o(e,s)})}}const J=new ht,vt=S({emits:["startUpgrade","resetUpgrade"],setup(t,{expose:e,emit:s}){const o=O({selectedRowKeys:[],loading:!1,data:[],startUpgrade:!1,startText:"Start",finish:!1}),a=F(),l=()=>{if(o.finish){console.log("back to device"),s.call(this,"resetUpgrade");return}o.startUpgrade=!0,o.startText="Starting",s.call(this,"startUpgrade")},m=()=>{o.startUpgrade=!1,o.startText="Back",o.finish=!0};e({resetProgress:m}),J.$on("update",(d,p)=>{console.log("update payload= topic="+d+"payload= "+p);const n=d.split("/");console.log("mac= "+n[n.length-2]);const u=JSON.parse(p.toString());console.log(u);const y=a.selectedDevices.filter(x=>a.upgradeMac.indexOf(x.mac)!==-1);console.log("target devices"),console.log(y);const _=y.find(x=>x.mac===n[n.length-2]);console.log("target device"),console.log(_),_&&(G.exports.isNumber(u.data.process)&&_.progress!==u.data.process&&(_.progress=u.data.process,console.log("update progress "+u.data.process)),G.exports.isNumber(u.data.state)&&_.state!==u.data.state&&(_.state=u.data.state,console.log("update state "+u.data.state))),h()&&(console.log("upgrade finish"),m())});const h=()=>{let d=!0;const p=a.selectedDevices.filter(n=>a.upgradeMac.indexOf(n.mac)!==-1);for(let n=0;n<p.length;n++)console.log("progress= "+p[n].progress+" state= "+p[n].state),(p[n].progress!==100||p[n].state!==1)&&(d=!1);return console.log("checkUpgradeFinish "+d),d};return(d,p)=>{const n=j,u=be,y=T,_=se,x=H,$=q;return f(),w($,{justify:"center"},{default:r(()=>[c(_,{span:24,style:{"margin-top":"40px"}},{default:r(()=>[c(y,{columns:i(nt),showHeader:!0,"data-source":i(a).selectedDevices.filter(v=>i(a).upgradeMac.indexOf(v.mac)!==-1),loading:i(o).loading,pagination:{pageSize:5}},{configured:r(({text:v})=>[g("span",null,[(f(),w(n,{key:v,color:v?"green":"volcano"},{default:r(()=>[k(D(v?"Configured":"No Configure"),1)]),_:2},1032,["color"]))])]),connected:r(({text:v})=>[g("span",null,[(f(),w(n,{key:v,color:v?"green":"volcano"},{default:r(()=>[k(D(v?"Online":"Offline"),1)]),_:2},1032,["color"]))])]),state:r(({text:v})=>[g("span",null,[(f(),w(n,{key:v,color:v===1?"green":v===0?"volcano":"geekblue"},{default:r(()=>[k(D(i(K)(v)),1)]),_:2},1032,["color"]))])]),progress:r(({text:v})=>[c(u,{percent:v,size:"small"},null,8,["percent"])]),_:1},8,["columns","data-source","loading"])]),_:1}),c(x,{type:"primary",loading:i(o).startUpgrade,size:"large",shape:"round",style:{width:"120px","margin-top":"40px"},onClick:l},{default:r(()=>[k(D(i(o).startText),1)]),_:1},8,["loading"])]),_:1})}}});const wt=k(" Previous"),yt=k(" Next"),bt=S({setup(t){const e=O({selectedRowKeys:[],loading:!1,data:[],fileName:"",showUploadFirmware:null,currentStep:0,selectDevices:[]}),s=N(),o=F(),a=()=>{e.currentStep!==0&&e.currentStep--},l=()=>{if(console.log("click select step= "+e.currentStep),e.currentStep===0&&e.fileName===""&&L.warn("Please select firmware firstly."),e.currentStep===1&&e.selectDevices.length===0){L.warn("Please select devices which you want to upgrade.");return}e.currentStep++},m=n=>{console.log("select firmware "+n),e.fileName=n,o.addSelectFirmware(n)},h=n=>{console.log(n),e.selectDevices=n,o.addUpgradeMac(n)},d=async()=>{var u;const n=await dt(e.fileName,e.selectDevices);console.log(n),le(n,"Upgrade has started!"),(n==null?void 0:n.code)!==0&&((u=s.value)==null||u.resetProgress())},p=()=>{e.currentStep=0,e.selectDevices=[],e.fileName="",o.resetAllDeviceProgress(),o.deleteUpgradeMac(),o.deleteSelectFirmware()};return(n,u)=>{const y=ke,_=xe,x=se,$=q,v=H;return f(),C(E,null,[c($,{class:"upgrade-steps",justify:"center",style:{"margin-top":"20px"}},{default:r(()=>[c(x,{span:22},{default:r(()=>[c(_,{current:i(e).currentStep,direction:"horizontal"},{default:r(()=>[c(y,{title:"Select firmware",description:"Select which version to upgrade."}),c(y,{title:"Select device",description:"Select devices to upgrade."}),c(y,{title:"Upgrade",description:"Confirm to upgrade."})]),_:1},8,["current"])]),_:1})]),_:1}),c($,{justify:"center",style:{"margin-top":"40px"}},{default:r(()=>[i(e).currentStep===0?(f(),w(x,{key:0,span:22},{default:r(()=>[c(mt,{onSelectedFirmware:m})]),_:1})):M("",!0),i(e).currentStep===1?(f(),w(x,{key:1,span:22},{default:r(()=>[c(gt,{onSelectDevices:h})]),_:1})):M("",!0),i(e).currentStep===2?(f(),w(x,{key:2,span:22},{default:r(()=>[c(vt,{onStartUpgrade:d,onResetUpgrade:p,ref_key:"upgradeProgressTable",ref:s},null,512)]),_:1})):M("",!0)]),_:1}),c($,{justify:"center",style:{"margin-top":"10px"}},{default:r(()=>[g("div",null,[i(e).currentStep>0&&i(e).currentStep<2?(f(),w(v,{key:0,type:"primary",size:"large",shape:"round",style:{"margin-right":"50px",width:"120px"},onClick:a},{default:r(()=>[wt]),_:1})):M("",!0),i(e).currentStep<2?(f(),w(v,{key:1,type:"primary",size:"large",shape:"round",style:{width:"120px"},onClick:l},{default:r(()=>[yt]),_:1})):M("",!0)])]),_:1}),c(ie,{ref:"showModalRef"},null,512)],64)}}});var kt=I(bt,[["__scopeId","data-v-bd4225d2"]]);const xt=S({name:"Configuration",setup(){console.log("setup")}});function St(t,e,s,o,a,l){return f(),C("div",null,"Configuration")}var Dt=I(xt,[["render",St]]);const $t=S({name:"Script",setup(){console.log("setup")}});function Lt(t,e,s,o,a,l){return f(),C("div",null,"Script")}var Ct=I($t,[["render",Lt]]);const Ut=S({name:"Device",setup(){console.log("setup")}});function Mt(t,e,s,o,a,l){return f(),C("div",null,"Help")}var Ot=I(Ut,[["render",Mt]]);const It=S({setup(){console.log("dashboard")}});function Ft(t,e,s,o,a,l){return f(),C("div",null," Dashboard ")}var At=I(It,[["render",Ft]]);const de=t=>(oe("data-v-03476488"),t=t(),ne(),t),Nt={class:"login-container"},Pt=de(()=>g("h2",{class:"login-title"},"Wiser Zigbee Launcher",-1)),Rt=de(()=>g("h2",{class:"title"},"Sign In",-1)),Tt=k("SIGN IN"),qt=S({setup(t){const e=O({userName:"",password:"",ip:"",loginStart:!1}),s=V(),o=z(),a=n=>{console.log(n,e)},l=n=>{console.log(n)},m=()=>{e.loginStart=!0,e.userName==="admin"&&e.password==="admin"?setTimeout(()=>{localStorage.setItem("accessToken","1234567890"),o.addUser({userName:e.userName,password:e.password,ips:[e.ip],currentIP:e.ip}),s.push("/home/device"),e.loginStart=!1},500):((e.userName!=="admin"||e.password!=="admin")&&L.error("Username or password error."),e.loginStart=!1)},p={checkUserName:[{validator:async(n,u)=>{if(u==="")return Promise.reject("Please input username")},trigger:"change"}],checkPassword:[{validator:async(n,u)=>{if(u==="")return Promise.reject("Please input password")},trigger:"change"}]};return(n,u)=>{const y=Le,_=Ce,x=Ue,$=H,v=Me,b=Se;return f(),C("div",Nt,[Pt,c(b,{class:"login-card"},{default:r(()=>[c(v,{model:i(e),rules:p,onFinish:a,onFinishFailed:l},{default:r(()=>[Rt,c(_,null,{default:r(()=>[c(y,{class:"inputBox",value:i(e).userName,"onUpdate:value":u[0]||(u[0]=A=>i(e).userName=A),placeholder:"Username"},{prefix:r(()=>[c(i(De),{style:{color:"rgba(0, 0, 0, 0.25)"}})]),_:1},8,["value"])]),_:1}),c(_,null,{default:r(()=>[c(x,{class:"inputBox",value:i(e).password,"onUpdate:value":u[1]||(u[1]=A=>i(e).password=A),placeholder:"Password"},{prefix:r(()=>[c(i($e),{style:{color:"rgba(0, 0, 0, 0.25)"}})]),_:1},8,["value"])]),_:1}),c(_,null,{default:r(()=>[c($,{class:"submit",type:"primary",onClick:m,disabled:i(e).userName===""||i(e).password==="",loading:i(e).loginStart},{default:r(()=>[Tt]),_:1},8,["disabled","loading"])]),_:1})]),_:1},8,["model"])]),_:1})])}}});var Ht=I(qt,[["__scopeId","data-v-03476488"]]);const jt={class:"demo-dropdown-wrap"},Et=k("U"),Bt=k(" Log out "),Kt=S({setup(t){const e=V(),s=F(),o=z(),a=({key:l})=>{console.log(`Click on item ${l}`),l==="logout"&&(localStorage.setItem("accessToken",""),s.deleteAllDevice(),o.deleteUser(),e.push("/login"))};return(l,m)=>{const h=Ie,d=ae,p=re,n=Fe;return f(),C("div",jt,[c(n,null,{overlay:r(()=>[c(p,{onClick:a},{default:r(()=>[c(d,{key:"logout"},{default:r(()=>[c(i(Oe)),Bt]),_:1})]),_:1})]),default:r(()=>[c(h,{style:{color:"#f56a00","background-color":"#fde3cf"}},{default:r(()=>[Et]),_:1})]),_:1})])}}});class zt{constructor(e,s,o,a){U(this,"mqclient");U(this,"brokerHost");U(this,"brokerPort");U(this,"endpoint");U(this,"protocol");U(this,"subscribeTopics");U(this,"subscribeCallbacks");this.brokerHost=e,this.brokerPort=s,this.endpoint=o,this.protocol=a,this.subscribeTopics=[],this.subscribeCallbacks=new Map}subscribe(e,s){this.subscribeTopics.push({topic:e,qos:s}),this.is_connected()&&this.mqclient.subscribe(e,{qos:s})}set_message_callback(e,s){this.subscribeCallbacks.set(e,s)}is_connected(){return this.mqclient.connected===!0}connect(e){try{this.mqclient=Ae.exports.connect(`${this.protocol}://${this.brokerHost}:${this.brokerPort}${this.endpoint}`,e)}catch(s){console.error(s)}this.mqclient.on("connect",()=>{console.log(`connect success to mqtt server[${this.brokerHost}:${this.brokerPort}]`);for(let s=0;s<this.subscribeTopics.length;s++){const o=this.subscribeTopics[s];this.mqclient.subscribe(o.topic,{qos:o.qos})}}),this.mqclient.on("message",(s,o)=>{console.log("topic= "+s),this.subscribeCallbacks.forEach((a,l)=>{s.indexOf(l)!==-1&&a(s,o)})}),this.mqclient.on("error",()=>{console.log("connect failure to mqtt server")})}}const Wt=S({setup(t,{expose:e}){const s=(a,l)=>{console.log(`update=>${l}`),J.$emit(a,l)};return e({connectMqtt:async a=>{console.log("connectMqtt");const l=new zt(a.host,a.port,a.endpoint,a.protocol);l.connect({username:a.user,password:a.pwd,clientId:a.id,clean:a.clean,connectTimeout:a.connectTimeout,reconnectPeriod:a.reconnectPeriod}),l.subscribe("v1.0/+/simulator/devices/+/update",0),l.subscribe("v1.0/+/simulator/devices/+/info",0),l.set_message_callback("update",s.bind(this)),l.set_message_callback("info",s.bind(this))}}),(a,l)=>(f(),C("div"))}});const P=t=>(oe("data-v-6ba0162a"),t=t(),ne(),t),Vt=P(()=>g("div",{class:"app-logo"},"WZL",-1)),Qt=P(()=>g("span",null,"Device",-1)),Jt=P(()=>g("span",null,"Update",-1)),Zt=P(()=>g("span",null,"Configure",-1)),Gt=P(()=>g("span",null,"Log",-1)),Xt=P(()=>g("span",null,"Help",-1)),Yt=S({setup(t){const e=V(),s=O({collapsed:!1,selectedKeys:[]}),o=N(),a=F(),l=z(),m=e.currentRoute.value.path;(m==="/"||m==="/home/device")&&e.push("/home/device"),R(()=>{var p;console.log("on mounted");let d={host:"localhost",port:8083,endpoint:"/mqtt",protocol:"ws",user:"",pwd:"",id:"mqttx_11c82570",clean:!0,connectTimeout:3e4,reconnectPeriod:3e4};(p=o.value)==null||p.connectMqtt(d),window.addEventListener("beforeunload",n=>h(n))});const h=d=>{console.log("close browser"),a.resetAllDeviceProgress(),a.deleteSelectFirmware(),a.deleteUpgradeMac(),l.deleteUser()};return Ne(()=>{window.removeEventListener("beforeunload",d=>h())}),J.$on("info",(d,p)=>{console.log("info payload= topic="+d+"payload= "+p);const n=d.split("/");console.log("mac= "+n[n.length-2]);const u=JSON.parse(p.toString()),y=a.deviceList.find(_=>_.mac===n[n.length-2]);console.log("target device"),console.log(u),y&&a.updateDevice(u.data)}),(d,p)=>{const n=W("router-link"),u=ae,y=re,_=Ee,x=q,$=Be,v=W("router-view"),b=Ke,A=Pe;return f(),C(E,null,[c(A,{class:"app-wrapper"},{default:r(()=>[c(_,{collapsed:i(s).collapsed,"onUpdate:collapsed":p[0]||(p[0]=fe=>i(s).collapsed=fe),theme:"light",collapsible:"",class:""},{default:r(()=>[Vt,c(y,{selectedKeys:[i(e).currentRoute.value.path],theme:"light",mode:"inline"},{default:r(()=>[c(u,{key:"/home/device"},{default:r(()=>[c(n,{to:"/home/device"}),c(i(Re)),Qt]),_:1}),c(u,{key:"/home/update"},{default:r(()=>[c(n,{to:"/home/update"}),c(i(Te)),Jt]),_:1}),c(u,{key:"/home/configure"},{default:r(()=>[c(n,{to:"/home/configure"}),c(i(qe)),Zt]),_:1}),c(u,{key:"/home/automation"},{default:r(()=>[c(n,{to:"/home/automation"}),c(i(He)),Gt]),_:1}),c(u,{key:"/home/help"},{default:r(()=>[c(n,{to:"/home/help"}),c(i(je)),Xt]),_:1})]),_:1},8,["selectedKeys"])]),_:1},8,["collapsed"]),c(A,null,{default:r(()=>[c($,{class:"app-header"},{default:r(()=>[c(x,{justify:"end",align:"middle"},{default:r(()=>[c(Kt)]),_:1})]),_:1}),c(b,{class:"app-content"},{default:r(()=>[c(v)]),_:1})]),_:1})]),_:1}),c(Wt,{ref_key:"mqttConnection",ref:o},null,512)],64)}}});var es=I(Yt,[["__scopeId","data-v-6ba0162a"]]);const ts=[{path:"/",redirect:"/home/device",name:"default"},{path:"/login",name:"Login",component:Ht},{path:"/home",name:"Home",component:es,redirect:"/home/device",meta:{requiresAuth:!0},children:[{path:"/home/dashboard",name:"Dashboard",component:At},{path:"/home/device",name:"Device",component:lt},{path:"/home/update",name:"Update",component:kt},{path:"/home/configure",name:"Configure",component:Dt},{path:"/home/automation",name:"Automation",component:Ct},{path:"/home/help",name:"Help",component:Ot}]}],ue=ze({history:We(),routes:ts,scrollBehavior(t,e,s){return s||{top:0}}});ue.beforeEach((t,e,s)=>{const o=localStorage.getItem("accessToken")||"";t.matched.some(a=>a.meta.requiresAuth)?(console.log("token= "+o),o?s():s("/login")):s()});const pe=Ve(Ye);pe.config.globalProperties={BASE_URL:"./",MODE:"production",DEV:!1,PROD:!0};const _e=Qe();_e.use(Je);pe.use(ue).use(_e).mount("#app");
