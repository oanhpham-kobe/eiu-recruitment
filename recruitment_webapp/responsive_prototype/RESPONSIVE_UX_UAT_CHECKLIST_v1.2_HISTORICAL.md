# Responsive UX-UAT Checklist — Prototype v1.2

Baseline: Full Handover v1.8 + Design System v1.7.

## Candidate — mobile go-live UX target
- [ ] Login readable and usable at 375px without horizontal page scroll.
- [ ] OTP/candidate login action is full-width on phone.
- [ ] Phiếu của tôi renders compact structured cards on phone.
- [ ] NEW submission exposes Edit; historical/non-editable submissions do not imply editability.
- [ ] Candidate Form remains one business page, one column on phone.
- [ ] Education repeatable block is easy to scan and add/remove.
- [ ] Upload controls are phone-friendly; whitelist/max 5 files/5 MB/CV required is visible.
- [ ] Pending file-change explanation is visible.
- [ ] Privacy Notice version + acknowledgement appears before Submit.
- [ ] Submit/Cancel actions remain reachable near the bottom of the viewport.
- [ ] VI/EN labels do not clip.

## Internal — mobile
- [ ] Hamburger opens off-canvas navigation; close/backdrop works.
- [ ] Page title is not ellipsized/clipped.
- [ ] Primary toolbar actions remain reachable on narrow width.
- [ ] Search stays visible; filters open as bottom sheet.
- [ ] Application Inbox structured rows retain Name/Email/DOB/Gender/Phone/Status/HR Note/Action.
- [ ] Historical Submission rows remain visually subordinate to parent Candidate.
- [ ] Detail Drawer becomes full-screen.
- [ ] Modal becomes bottom sheet/full-width where appropriate.
- [ ] Touch controls are at least ~44px high for core mobile interactions.

## Tablet portrait 768px
- [ ] Sidebar is off-canvas.
- [ ] Wide operational table remains a table, not a compressed card grid.
- [ ] Native horizontal scroll works.
- [ ] Sticky identity columns preserve context.
- [ ] Search + filter controls remain visible.
- [ ] Drawer width is approximately 70–88vw, not an impossible desktop min/max combination.

## Tablet landscape 1024px
- [ ] Off-canvas navigation works.
- [ ] Toolbar can scroll/wrap without clipping actions.
- [ ] Table horizontal overflow is contained inside the table shell, not the whole page.
- [ ] No page-level horizontal scroll.

## Accessibility
- [ ] 16px operational text remains readable.
- [ ] Status is textual, not color-only.
- [ ] Keyboard expand controls remain semantic.
- [ ] Focus outline remains visible.
- [ ] Full-screen drawer/modal has an explicit close control.
- [ ] No normal VI/EN page title is clipped.

## Out of scope for this prototype pass
- Backend/RLS/Storage/Auth implementation.
- Real server-side pagination/filtering.
- Real upload/malware processing.
- Production email/PDF behavior.
- Pixel approval of official EIU PDF template.
