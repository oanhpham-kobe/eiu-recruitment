/* Responsive Prototype v1.8 — External Review v9 scheduling/copy alignment. */
function isoDateV18(d){if(!d)return ''; if(/^\d{4}-\d{2}-\d{2}$/.test(d))return d; const m=d.match(/^(\d{2})\/(\d{2})\/(\d{4})$/); return m?`${m[3]}-${m[2]}-${m[1]}`:'';}
function displayDateV18(d){if(!d)return ''; if(/^\d{2}\/\d{2}\/\d{4}$/.test(d))return d; const m=d.match(/^(\d{4})-(\d{2})-(\d{2})$/); return m?`${m[3]}/${m[2]}/${m[1]}`:d;}
function isStructurallyEmptyRoundV18(r){return !!r&&r.no===1&&r.active!==false&&!r.topic&&!r.date&&!r.start&&!r.end&&!r.format&&!r.location&&(!r.participants||!r.participants.length)&&!r.note&&!r.copiedFromInterviewId&&!state.applications.some(a=>a.rounds.some(x=>x.copiedFromInterviewId===r.id));}
function conflictKindsV18(targetApp,srcId,date,start,end,location,parts){
 const kinds=new Set();
 for(const otherApp of state.applications){for(const r of otherApp.rounds){
  if(r.id===srcId||!r.active||r.status==='CANCELLED'||!r.date||!r.start||!r.end)continue;
  if(isoDateV18(r.date)!==isoDateV18(date)||!(start<r.end&&end>r.start))continue;
  if(otherApp.candidateId===targetApp.candidateId)kinds.add('Candidate');
  const roomA=(location||'').trim(),roomB=(r.location||'').trim();
  if(roomA&&roomB&&roomA===roomB&&!/meet|online/i.test(roomA))kinds.add('Room');
  if((r.participants||[]).some(p=>parts.includes(p)))kinds.add('Interviewer');
 }} return [...kinds];
}
function allCurrentParticipantsActiveV18(round){return !round||!(round.participants||[]).some(uid=>!state.users[uid]||state.users[uid].active===false);}

roundModal=function(m){
 let sourceApp=appById(m.data?.appId||state.expandedApplication||'a1'),src=m.data?.roundId?roundById(m.data.roundId):currentRound(sourceApp),copy=m.type==='copyRound',edit=m.type==='editRound';
 const no=edit?src.no:Math.max(0,...sourceApp.rounds.map(r=>r.no))+1;
 const dateVal=copy?isoDateV18(src?.date):edit?isoDateV18(src?.date):'2025-06-15';
 return modalFrame(copy?tx('Sao chép lịch phỏng vấn','Copy interview'):edit?tx('Chỉnh sửa lịch phỏng vấn','Edit interview'):tx('Tạo lịch phỏng vấn','Create interview'),`<div class="form-grid"><div class="field wide"><label>Application</label><select id="roundApp" class="select"><option value="${sourceApp.id}">${candidate(sourceApp.candidateId).name} — ${sourceApp.position}</option>${state.applications.filter(x=>x.id!==sourceApp.id).map(x=>`<option value="${x.id}">${candidate(x.candidateId).name} — ${x.position}</option>`).join('')}</select></div><div class="field"><label>${tx('Vòng','Round')}</label><input id="roundNo" class="input" value="${no}" disabled></div><div class="field"><label>Demo Topic</label><input id="roundTopic" class="input" value="${copy?'':src?.topic||''}" placeholder="${tx('Vòng mới để trống','New round stays blank')}"></div><div class="field"><label>${tx('Ngày','Date')} *</label><input id="roundDate" class="input" type="date" value="${dateVal}"></div><div class="field"><label>${tx('Giờ bắt đầu','Start time')} *</label><input id="roundStart" class="input" type="time" value="${copy||edit?src?.start||'09:00':'09:00'}"></div><div class="field"><label>${tx('Giờ kết thúc','End time')} *</label><input id="roundEnd" class="input" type="time" value="${copy||edit?src?.end||'10:00':'10:00'}"></div><div class="field"><label>${tx('Hình thức','Format')}</label><select id="roundFormat" class="select"><option ${src?.format==='Trực tiếp'?'selected':''}>Trực tiếp</option><option ${src?.format==='Online'?'selected':''}>Online</option></select></div><div class="field"><label>${tx('Địa điểm','Location')}</label><input id="roundLocation" class="input" value="${copy||edit?src?.location||'':'Phòng 11.101.B5'}"></div><div class="field wide"><label>${tx('Người tham dự','Participants')}</label><select id="roundParticipants" class="select"><option value="u1,u2,u3">TS. Trần Minh Khoa; ThS. Lê Hoàng Nam; ThS. Phạm Quỳnh Anh</option><option value="u1,u4">TS. Trần Minh Khoa; ThS. Trần Thu Hương</option></select></div></div><div id="conflictBox"></div>`,`<button class="btn" onclick="closeModal()">${tx('Hủy','Cancel')}</button><button class="btn primary" onclick="saveRound('${m.type}','${src?.id||''}')">${tx('Xác nhận','Confirm')}</button>`);
};

saveRound=function(type,srcId){
 const targetApp=appById($('#roundApp').value),src=srcId?roundById(srcId):null,date=displayDateV18($('#roundDate').value),start=$('#roundStart').value,end=$('#roundEnd').value,location=$('#roundLocation').value,parts=$('#roundParticipants').value.split(',').filter(Boolean),format=$('#roundFormat')?.value||'Trực tiếp';
 const sourceApp=src?.application;
 if(type==='editRound'&&!allCurrentParticipantsActiveV18(findRound(srcId))){$('#conflictBox').innerHTML=`<div class="alert">CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED</div>`;return;}
 const kinds=conflictKindsV18(targetApp,srcId,date,start,end,location,parts);
 if(kinds.length){$('#conflictBox').innerHTML=`<div class="alert">${tx('Xung đột lịch','Schedule conflict')}: ${kinds.join(' + ')}. ${tx('Không thể xác nhận.','Confirmation is blocked.')}</div>`;return;}
 const values={topic:$('#roundTopic').value,date,start,end,format,location,status:'AVAILABLE',note:'',participants:parts,active:true};
 if(type==='editRound'){Object.assign(findRound(srcId),values);}
 else if(type==='copyRound'&&sourceApp&&targetApp.id!==sourceApp.id){
   const r1=targetApp.rounds.find(r=>r.no===1);
   if(isStructurallyEmptyRoundV18(r1)){Object.assign(r1,values,{no:1,topic:'',copiedFromInterviewId:srcId});}
   else{const no=Math.max(0,...targetApp.rounds.map(r=>r.no))+1;targetApp.rounds.push({id:'r'+Date.now(),no,...values,topic:'',copiedFromInterviewId:srcId});}
 } else {const no=Math.max(0,...targetApp.rounds.map(r=>r.no))+1;targetApp.rounds.push({id:'r'+Date.now(),no,...values,topic:type==='copyRound'?'':values.topic,copiedFromInterviewId:type==='copyRound'?srcId:null});}
 closeModal();toast(type==='copyRound'?tx('Đã sao chép lịch theo rule Round 1','Interview copied with Round 1 rule'):tx('Đã lưu lịch phỏng vấn','Interview saved'));render();
};
const _shellV18=shell;shell=function(content,title,sub=''){return _shellV18(content,title,sub).replace(/Responsive UX-UAT v1\.7/g,'Responsive UX-UAT v1.8');};
const _loginPageV18=loginPage;loginPage=function(){return _loginPageV18().replace(/Responsive UX-UAT v1\.7/g,'Responsive UX-UAT v1.8');};
render();
