# 🎯 CrisisGrid AI - Citizen Portal Staged Implementation Plan

## Overview
This plan implements the Citizen Portal in 12 stages with component-level testing using Playwright MCP server and security validation at each stage.

## Current Progress (30% Complete)
✅ **Foundation Layer Complete:**
- Custom Hooks: useGeolocation, useMediaUpload, useReportForm, useNearbyAlerts
- UI Components: StatusBadge, SeverityBadge, CrisisIcon, LoadingSpinner, EmptyState, ErrorAlert, RiskLevelBadge
- Map Components: BaseMap, LocationMarker
- API Infrastructure: Complete with React Query hooks

## Remaining Work (70%)

### Stage 1: MCP Setup + Citizen Layout (Priority: CRITICAL)
**Components to Build:**
- `src/app/citizen/layout.tsx` - Citizen-specific layout with navigation
- MCP Configuration for testing

**Testing Checklist:**
- [ ] Navigation renders correctly
- [ ] Emergency button always visible
- [ ] Mobile responsive
- [ ] Breadcrumbs work
- [ ] Security: No XSS in navigation items

**Deliverables:**
- Working citizen layout
- MCP test configuration

---

### Stage 2: Form Components (Priority: CRITICAL)
**Components to Build:**
- `src/components/forms/ReportForm.tsx` - Main report submission form
- `src/components/forms/CrisisTypeSelector.tsx` - Crisis type dropdown with icons
- `src/components/forms/LocationPicker.tsx` - Interactive map-based location picker
- `src/components/forms/MediaUpload.tsx` - Drag-and-drop file upload with preview

**Testing Checklist:**
- [ ] All form validations work (20-1000 chars, required fields)
- [ ] Crisis type selector shows icons
- [ ] Location picker integrates with map
- [ ] File upload validates types (jpg, png, gif, mp4, mov) and size (10MB)
- [ ] Preview thumbnails display correctly
- [ ] Security: Input sanitization, file type validation, XSS prevention

**Security Focus:**
- SQL injection in text fields
- XSS in description field
- File upload validation bypass attempts
- Oversized file handling

---

### Stage 3: Card Components (Priority: HIGH)
**Components to Build:**
- `src/components/cards/ReportCard.tsx` - Report summary display
- `src/components/cards/AlertCard.tsx` - Alert summary display
- `src/components/cards/AdvisoryCard.tsx` - Safety advisory display
- `src/components/cards/QuickActionCard.tsx` - Action button cards
- `src/components/cards/SafetyActions.tsx` - Priority-ordered actions list

**Testing Checklist:**
- [ ] Cards render with correct data
- [ ] Status badges display correctly
- [ ] Click handlers work
- [ ] Responsive on mobile
- [ ] Security: No script injection via card content

---

### Stage 4: Report Submission Flow (Priority: CRITICAL)
**Pages to Build:**
- `src/app/citizen/report/page.tsx` - Report submission page

**Testing Checklist:**
- [ ] Form submission works end-to-end
- [ ] Loading states display during submission
- [ ] Success notification appears
- [ ] Error handling works
- [ ] Anonymous toggle works
- [ ] Contact info validation (if not anonymous)
- [ ] Location auto-detect works
- [ ] Media upload completes
- [ ] Security: All inputs validated, no sensitive data in console

**User Flow Test:**
1. Navigate to report page
2. Select crisis type
3. Enter description (test min/max length)
4. Pick location (auto-detect + manual)
5. Upload media (test valid/invalid files)
6. Toggle anonymous
7. Submit report
8. Verify success message

---

### Stage 5: My Reports Page (Priority: HIGH)
**Pages to Build:**
- `src/app/citizen/reports/page.tsx` - List of user's reports

**Testing Checklist:**
- [ ] Reports list displays
- [ ] List/grid view toggle works
- [ ] Status filters work
- [ ] Search functionality works
- [ ] Click to view details works
- [ ] Empty state displays when no reports
- [ ] Security: User can only see their own reports

---

### Stage 6: Report Detail Page (Priority: HIGH)
**Pages to Build:**
- `src/app/citizen/reports/[id]/page.tsx` - Single report details
- `src/components/maps/ReportMap.tsx` - Map for single report

**Testing Checklist:**
- [ ] Report details display correctly
- [ ] Verification status shows
- [ ] Timeline renders
- [ ] Map shows report location
- [ ] Related alerts display (if any)
- [ ] Actions work (view on map, get advice)
- [ ] Security: Cannot access other users' reports

---

### Stage 7: Safety Advisory Page (Priority: HIGH)
**Pages to Build:**
- `src/app/citizen/advisory/page.tsx` - Safety advisories
- `src/components/maps/AdvisoryMap.tsx` - Map with risk radius

**Testing Checklist:**
- [ ] Advisories display by location
- [ ] Search by incident ID works
- [ ] Risk level badges show correctly
- [ ] Priority actions ordered correctly
- [ ] Expandable sections work
- [ ] Map shows incident location and radius
- [ ] Emergency contacts display
- [ ] Security: No injection in advisory content

---

### Stage 8: Nearby Alerts Page (Priority: MEDIUM)
**Pages to Build:**
- `src/app/citizen/alerts/page.tsx` - Active alerts near user
- `src/components/maps/AlertsMap.tsx` - Map showing multiple alerts

**Testing Checklist:**
- [ ] Geolocation permission requested
- [ ] Alerts filtered by distance
- [ ] Distance calculation correct
- [ ] Map shows all alerts
- [ ] Filter by crisis type works
- [ ] Filter by severity works
- [ ] Real-time updates work (30s interval)
- [ ] Security: Location data handled securely

---

### Stage 9: Emergency Contacts Page (Priority: MEDIUM)
**Pages to Build:**
- `src/app/citizen/contacts/page.tsx` - Emergency contact information

**Testing Checklist:**
- [ ] Contact cards display
- [ ] Quick dial buttons work
- [ ] Search functionality works
- [ ] Location-based contacts show (if available)
- [ ] Security: No sensitive contact data exposed

---

### Stage 10: Citizen Home Page (Priority: HIGH)
**Pages to Build:**
- Update `src/app/citizen/page.tsx` - Main citizen portal page

**Testing Checklist:**
- [ ] Hero section displays
- [ ] Quick action cards work
- [ ] Recent alerts show (if location available)
- [ ] Safety tips carousel works
- [ ] All navigation links work
- [ ] Security: No XSS in dynamic content

---

### Stage 11: Security Audit & Integration Testing (Priority: CRITICAL)
**Focus Areas:**
1. **Input Validation**
   - Test all forms with malicious payloads
   - SQL injection attempts
   - XSS attempts
   - Buffer overflow attempts

2. **Authentication & Authorization**
   - Verify role-based access
   - Test unauthorized access attempts

3. **Data Exposure**
   - Check API responses for sensitive data
   - Verify no tokens/secrets in console
   - Check network tab for leaks

4. **CORS & API Security**
   - Verify CORS configuration
   - Test API error handling

5. **Map Security**
   - Validate lat/lng constraints
   - Test script injection via map

**Testing Checklist:**
- [ ] All OWASP Top 10 checks performed
- [ ] No critical vulnerabilities found
- [ ] All medium issues documented
- [ ] Recommendations provided

---

### Stage 12: Documentation & Reports (Priority: HIGH)
**Deliverables:**
1. `UI_TEST_REPORT.md` - Complete UI test results
2. `SECURITY_REPORT.md` - Security audit findings
3. `BUG_REPORT.md` - Known issues and fixes

**Report Structure:**

#### UI_TEST_REPORT.md
- Tested flows
- Pass/fail status
- Screenshots/observations
- UX improvements

#### SECURITY_REPORT.md
- Critical issues (with fixes)
- Medium issues
- Low issues
- Passed checks
- Recommendations

#### BUG_REPORT.md
- Reproducible bugs
- Steps to reproduce
- Expected vs actual behavior
- Priority level

---

## Implementation Strategy

### Build-Test-Fix Cycle
For each stage:
1. **Build** components in code mode
2. **Test** with Playwright MCP (functional + security)
3. **Fix** issues found
4. **Document** results
5. **Move to next stage**

### Testing Protocol
- Use Playwright MCP for all UI testing
- Test both happy path and edge cases
- Perform security testing at each stage
- Document all findings immediately

### Success Criteria
- ✅ All pages functional
- ✅ All forms validated
- ✅ No critical security issues
- ✅ Mobile responsive
- ✅ Error handling complete
- ✅ Loading states implemented
- ✅ Reports generated

---

## Estimated Timeline
- Stage 1: 30 min (layout + MCP setup)
- Stage 2: 1 hour (form components)
- Stage 3: 45 min (card components)
- Stage 4: 45 min (report submission + test)
- Stage 5: 30 min (my reports + test)
- Stage 6: 30 min (report detail + test)
- Stage 7: 45 min (advisory + test)
- Stage 8: 30 min (alerts + test)
- Stage 9: 20 min (contacts + test)
- Stage 10: 30 min (home page + test)
- Stage 11: 1 hour (security audit)
- Stage 12: 30 min (documentation)

**Total: ~7 hours**

---

## Next Steps
1. Start with Stage 1 (MCP setup + layout)
2. Proceed sequentially through stages
3. Test thoroughly at each stage
4. Generate final reports

---

## Component Dependencies

### Stage Dependencies
```
Stage 1 (Layout)
    ↓
Stage 2 (Forms) + Stage 3 (Cards)
    ↓
Stage 4 (Report Submission) ← Uses Forms
    ↓
Stage 5 (My Reports) ← Uses Cards
    ↓
Stage 6 (Report Detail) ← Uses Cards + Maps
    ↓
Stage 7 (Advisory) ← Uses Cards + Maps
    ↓
Stage 8 (Alerts) ← Uses Cards + Maps
    ↓
Stage 9 (Contacts) ← Uses Cards
    ↓
Stage 10 (Home) ← Uses All Components
    ↓
Stage 11 (Security Audit)
    ↓
Stage 12 (Documentation)
```

### Reusable Components
These components will be used across multiple pages:
- **StatusBadge** - Reports, Alerts, Advisory
- **SeverityBadge** - Alerts, Reports
- **CrisisIcon** - All pages
- **LoadingSpinner** - All pages
- **EmptyState** - Reports, Alerts, Contacts
- **ErrorAlert** - All pages
- **RiskLevelBadge** - Advisory, Alerts
- **BaseMap** - All map views
- **LocationMarker** - All map views

---

## Testing Strategy Details

### Unit Testing (Per Component)
- Props validation
- Event handlers
- Conditional rendering
- Error states
- Loading states

### Integration Testing (Per Page)
- Component interactions
- Data flow
- Navigation
- Form submissions
- API calls

### E2E Testing (Per Flow)
- Complete user journeys
- Multi-page workflows
- Real API interactions
- Error recovery

### Security Testing (Per Stage)
- Input validation
- XSS prevention
- CSRF protection
- Authentication checks
- Authorization checks
- Data exposure checks

---

## MCP Testing Configuration

### Setup Requirements
1. Install Playwright MCP server
2. Configure test environment
3. Set up test data
4. Configure browser contexts

### Test Execution
```bash
# Run all tests
npm run test:e2e

# Run specific stage
npm run test:e2e -- --grep "Stage 1"

# Run with UI
npm run test:e2e -- --ui

# Generate report
npm run test:e2e -- --reporter=html
```

### Test Data
- Mock user accounts
- Sample reports
- Test alerts
- Mock geolocation data
- Sample media files

---

## Risk Mitigation

### High-Risk Areas
1. **File Upload** - Potential for malicious files
   - Mitigation: Strict validation, virus scanning, size limits
   
2. **Geolocation** - Privacy concerns
   - Mitigation: User consent, secure storage, no tracking
   
3. **Real-time Updates** - Performance issues
   - Mitigation: Throttling, efficient polling, WebSocket fallback
   
4. **Map Integration** - Third-party dependency
   - Mitigation: Error handling, fallback UI, offline support

### Medium-Risk Areas
1. **Form Validation** - Bypass attempts
   - Mitigation: Client + server validation, sanitization
   
2. **Anonymous Reports** - Abuse potential
   - Mitigation: Rate limiting, CAPTCHA, verification

---

## Performance Targets

### Page Load Times
- Initial load: < 2s
- Subsequent navigation: < 500ms
- Map rendering: < 1s
- Form submission: < 1s

### Bundle Size
- Initial bundle: < 200KB (gzipped)
- Route chunks: < 50KB each
- Total JS: < 500KB

### Lighthouse Scores
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 90
- SEO: > 90

---

## Accessibility Requirements

### WCAG 2.1 Level AA Compliance
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] Color contrast ratios
- [ ] Focus indicators
- [ ] ARIA labels
- [ ] Alt text for images
- [ ] Form labels
- [ ] Error messages

### Testing Tools
- axe DevTools
- WAVE
- Lighthouse
- Screen reader testing (NVDA/JAWS)

---

## Browser Support

### Desktop
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Mobile
- iOS Safari 14+
- Chrome Android 90+
- Samsung Internet 14+

### Testing Matrix
- Desktop: Chrome, Firefox, Safari
- Mobile: iOS Safari, Chrome Android
- Tablet: iPad Safari, Android Chrome

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Security audit complete
- [ ] Performance benchmarks met
- [ ] Accessibility audit complete
- [ ] Browser testing complete
- [ ] Documentation complete

### Deployment
- [ ] Environment variables set
- [ ] API endpoints configured
- [ ] CDN configured
- [ ] SSL certificates valid
- [ ] Monitoring enabled
- [ ] Error tracking enabled

### Post-Deployment
- [ ] Smoke tests passing
- [ ] Monitoring dashboards reviewed
- [ ] Error rates normal
- [ ] Performance metrics normal
- [ ] User feedback collected

---

## Maintenance Plan

### Daily
- Monitor error rates
- Check performance metrics
- Review user feedback

### Weekly
- Security updates
- Dependency updates
- Bug fixes

### Monthly
- Feature enhancements
- Performance optimization
- Accessibility improvements

---

## Success Metrics

### User Engagement
- Report submission rate
- Time to submit report
- Return user rate
- Feature usage

### Technical Metrics
- Error rate < 1%
- API response time < 500ms
- Page load time < 2s
- Uptime > 99.9%

### Security Metrics
- Zero critical vulnerabilities
- Zero data breaches
- Zero unauthorized access attempts

---

## Appendix

### Useful Commands
```bash
# Development
npm run dev

# Build
npm run build

# Test
npm run test
npm run test:e2e
npm run test:security

# Lint
npm run lint
npm run lint:fix

# Type check
npm run type-check

# Format
npm run format
```

### Environment Variables
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAP_API_KEY=your_key_here
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

### Key Files
- `src/app/citizen/layout.tsx` - Citizen layout
- `src/components/forms/ReportForm.tsx` - Main form
- `src/lib/api/reports.ts` - Report API
- `src/hooks/useReportForm.ts` - Form logic
- `src/types/api.ts` - Type definitions

---

**Document Version:** 1.0  
**Last Updated:** 2026-05-02  
**Author:** Bob (AI Software Engineer)  
**Status:** Ready for Implementation