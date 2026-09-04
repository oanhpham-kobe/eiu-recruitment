/* Responsive Prototype v1.10 — External Review v12 schedule-status operational-transition parity. */
function appForRoundV110(roundId){return state.applications.find(a=>(a.rounds||[]).some(r=>r.id===roundId))||null;}
function roundRefV110(roundId){const a=appForRoundV110(roundId);return a?(a.rounds||[]).find(r=>r.id===roundId)||null:null;}
function isOperationalStatusV110(status){return status!=='CANCELLED';}
function isResourceBlockingV110(app,round,statusOverride=null){
  if(!app||app.active===false||!round||round.active===false)return false;
  const status=statusOverride||round.status;
  return isOperationalStatusV110(status)&&!!round.date&&!!round.start&&!!round.end;
}
function inactiveParticipantsV110(round){return (round?.participants||[]).filter(uid=>!state.users[uid]||state.users[uid].active===false);}
function effectiveStatusV110(round,targetIds,targetStatus){return targetIds.has(round.id)?targetStatus:round.status;}
function conflictKindsForTransitionV110(targetApp,targetRound,targetIds,targetStatus){
  const kinds=new Set();
  if(!isResourceBlockingV110(targetApp,targetRound,targetStatus))return [];
  for(const otherApp of state.applications){
    for(const other of (otherApp.rounds||[])){
      if(other.id===targetRound.id)continue;
      const otherStatus=effectiveStatusV110(other,targetIds,targetStatus);
      if(!isResourceBlockingV110(otherApp,other,otherStatus))continue;
      if(isoDateV18(other.date)!==isoDateV18(targetRound.date)||!(targetRound.start<other.end&&targetRound.end>other.start))continue;
      if(otherApp.candidateId===targetApp.candidateId)kinds.add('Candidate');
      const roomA=(targetRound.location||'').trim(),roomB=(other.location||'').trim();
      if(roomA&&roomB&&roomA===roomB&&!/meet|online/i.test(roomA))kinds.add('Room');
      if((other.participants||[]).some(uid=>(targetRound.participants||[]).includes(uid)))kinds.add('Interviewer');
    }
  }
  return [...kinds];
}
function validateInterviewOperationalTransitionV110(roundIds,targetStatus){
  const ids=[...new Set(roundIds)].filter(Boolean),targetIds=new Set(ids),failures=[];
  for(const rid of ids){
    const app=appForRoundV110(rid),round=roundRefV110(rid);
    if(!app||!round){failures.push({roundId:rid,code:'INTERVIEW_NOT_FOUND'});continue;}
    if(isResourceBlockingV110(app,round,targetStatus)){
      const inactive=inactiveParticipantsV110(round);
      if(inactive.length){failures.push({roundId:rid,code:'CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED',participants:inactive});continue;}
      const conflicts=conflictKindsForTransitionV110(app,round,targetIds,targetStatus);
      if(conflicts.length)failures.push({roundId:rid,code:'SCHEDULE_CONFLICT',conflicts});
    }
  }
  return {ok:failures.length===0,failures};
}
function statusTransitionMessageV110(result){
  const f=result.failures[0]||{};
  if(f.code==='CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED')return `CURRENT_PARTICIPANT_INACTIVE_REASSIGN_REQUIRED${f.participants?.length?`: ${f.participants.map(uid=>state.users[uid]?.name||uid).join(', ')}`:''}`;
  if(f.code==='SCHEDULE_CONFLICT')return `${tx('Xung đột lịch','Schedule conflict')}: ${(f.conflicts||[]).join(' + ')}`;
  return f.code||tx('Không thể cập nhật trạng thái lịch.','Unable to update interview schedule status.');
}
function applyInterviewScheduleStatusV110(roundIds,targetStatus){
  const ids=[...new Set(roundIds)].filter(Boolean);
  if(!ids.length){toast(tx('Chọn ít nhất một lịch trước.','Select at least one interview.'));return false;}
  const validation=validateInterviewOperationalTransitionV110(ids,targetStatus);
  state.lastInterviewStatusTransitionV110={roundIds:[...ids],targetStatus,ok:validation.ok,failures:validation.failures.map(x=>({...x,participants:x.participants?[...x.participants]:undefined,conflicts:x.conflicts?[...x.conflicts]:undefined}))};
  state.statusMenu=null;
  if(!validation.ok){toast(statusTransitionMessageV110(validation));return false;}
  ids.forEach(rid=>{const r=roundRefV110(rid);if(r)r.status=targetStatus;});
  toast(ids.length>1?tx(`Đã cập nhật ${ids.length} lịch theo ALL_OR_NOTHING.`,`Updated ${ids.length} interviews with ALL_OR_NOTHING semantics.`):tx('Đã cập nhật Interview Schedule Status.','Interview Schedule Status updated.'));
  render();
  return true;
}
const _setEntityStatusV110Base=setEntityStatus;
setEntityStatus=function(entity,id,status){
  if(entity==='round')return applyInterviewScheduleStatusV110([id],status);
  if(entity==='bulk-interview')return applyInterviewScheduleStatusV110([...state.selectedIds],status);
  return _setEntityStatusV110Base(entity,id,status);
};
const _shellV110=shell;shell=function(content,title,sub=''){return _shellV110(content,title,sub).replace(/Responsive UX-UAT v1\.9/g,'Responsive UX-UAT v1.10');};
const _loginPageV110=loginPage;loginPage=function(){return _loginPageV110().replace(/Responsive UX-UAT v1\.9/g,'Responsive UX-UAT v1.10');};
render();
