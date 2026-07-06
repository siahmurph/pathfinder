const apiUrl = '/pathfinder/api'
const formLookup = document.getElementById('formlookup')
const formRule = document.getElementById('rule-form')
const routeOutput = document.getElementById('route-output')
const rulesList = document.getElementById('rules-list')
const ruleSearch = document.getElementById('rule-search')
const clearRuleBtn = document.getElementById('clear-rule-btn')
const saveRuleBtn = document.getElementById('save-rule-btn')
const formHeading = document.getElementById('rule-form-heading')

const fields = {
  id: document.getElementById('rule_id'),
  program_name: document.getElementById('program_name'),
  match_type: document.getElementById('match_type'),
  pattern: document.getElementById('pattern'),
  min_duration_sec: document.getElementById('min_duration_sec'),
  max_duration_sec: document.getElementById('max_duration_sec'),
  destination_1: document.getElementById('destination_1'),
  destination_2: document.getElementById('destination_2'),
  promo_possible: document.getElementById('promo_possible')
}

;(async function checkMaintenance () {
  try {
    const res = await fetch('/crusher/status.json', { cache: 'no-store' })
    if (!res.ok) return
    const status = await res.json()
    if (status.pathfinder?.enabled) {
      document.getElementById('main-content').classList.add('d-none')
      document.getElementById('maintenance-screen').classList.remove('d-none')
      document.getElementById('maintenance-message').textContent =
        status.pathfinder.message || 'Pathfinder is temporarily unavailable.'
    }
  } catch {
    /* show app normally */
  }
})()

// ── Destination label map ───────────────────────────────────────────────
const DEST_LABELS = {
  ignore: 'Ignore',
  barterWatch: 'Barter Movie',
  promoWatch: 'Promo',
  eiWatch: 'E/I Spotripper',
  standardProgWatch: 'Program'
}

function destLabel (val) {
  return val ? DEST_LABELS[val] || val : null
}

// ── Destination chips ────────────────────────────────────────────────────
function setupChipGroup (groupId, hiddenInputId) {
  const group = document.getElementById(groupId)
  if (!group) return
  group.querySelectorAll('.dest-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const wasActive = chip.classList.contains('dest-chip-active')
      group
        .querySelectorAll('.dest-chip')
        .forEach(c => c.classList.remove('dest-chip-active'))
      if (!wasActive) chip.classList.add('dest-chip-active')
      document.getElementById(hiddenInputId).value = wasActive
        ? ''
        : chip.dataset.value
    })
  })
}

function setDestChip (groupId, value) {
  const group = document.getElementById(groupId)
  if (!group) return
  group.querySelectorAll('.dest-chip').forEach(chip => {
    chip.classList.toggle(
      'dest-chip-active',
      !!value && chip.dataset.value === value
    )
  })
}

formLookup.addEventListener('submit', async event => {
  event.preventDefault()

  const payload = {
    title: formLookup.elements.title.value,
    alt_id: formLookup.elements.alt_id.value,
    filename: formLookup.elements.filename.value,
    duration_sec: null
  }

  try {
    const response = await fetch(apiUrl + '/route', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    const data = await response.json()
    routeOutput.textContent = JSON.stringify(data, null, 2)
  } catch {
    routeOutput.textContent = JSON.stringify(
      { error: 'Unable to reach the Pathfinder API.' },
      null,
      2
    )
  }
})

function nullableText (value) {
  const text = (value || '').trim()
  return text.length ? text : null
}

function nullableInt (value) {
  const text = (value || '').toString().trim()
  if (!text.length) return null
  const parsed = Number(text)
  return Number.isNaN(parsed) ? null : parsed
}

function getRulePayload () {
  return {
    program_name: fields.program_name.value.trim(),
    match_type: nullableText(fields.match_type.value),
    pattern: nullableText(fields.pattern.value),
    min_duration_sec: nullableInt(fields.min_duration_sec.value),
    max_duration_sec: nullableInt(fields.max_duration_sec.value),
    destination_1: nullableText(fields.destination_1.value),
    destination_2: nullableText(fields.destination_2.value),
    promo_possible: fields.promo_possible.checked ? 1 : 0
  }
}

function resetRuleForm () {
  formRule.reset()
  fields.id.value = ''
  saveRuleBtn.textContent = 'Save Rule'
  formHeading.textContent = 'Create Rule'
  setDestChip('destination_1_chips', null)
  setDestChip('destination_2_chips', null)
  const searchTerm = ruleSearch.value.trim()
  if (searchTerm) fields.program_name.value = searchTerm
}

function fillRuleForm (rule) {
  fields.id.value = rule.id
  fields.program_name.value = rule.program_name || ''
  fields.match_type.value = rule.match_type || ''
  fields.pattern.value = rule.pattern || ''
  fields.min_duration_sec.value = rule.min_duration_sec ?? ''
  fields.max_duration_sec.value = rule.max_duration_sec ?? ''
  fields.destination_1.value = rule.destination_1 || ''
  fields.destination_2.value = rule.destination_2 || ''
  setDestChip('destination_1_chips', rule.destination_1)
  setDestChip('destination_2_chips', rule.destination_2)
  fields.promo_possible.checked = Boolean(rule.promo_possible)
  saveRuleBtn.textContent = 'Update Rule'
  formHeading.textContent = 'Edit Rule'
}

async function loadRules (search = '') {
  const normalizedSearch = search.trim()
  const url = normalizedSearch.length
    ? `${apiUrl}/rules?program_name=${encodeURIComponent(normalizedSearch)}`
    : `${apiUrl}/rules`
  const response = await fetch(url)
  const rules = await response.json()

  if (!Array.isArray(rules) || !rules.length) {
    rulesList.innerHTML = '<div class="text-secondary">No rules found.</div>'
    return []
  }

  rulesList.innerHTML = rules
    .map(rule => {
      const d1 = destLabel(rule.destination_1)
      const d2 = destLabel(rule.destination_2)
      const chips = [
        rule.match_type
          ? `<span class="rule-chip rule-chip--type">${rule.match_type}</span>`
          : '',
        rule.pattern
          ? `<span class="rule-chip rule-chip--pattern">${rule.pattern}</span>`
          : '',
        d1 ? `<span class="rule-chip rule-chip--dest">${d1}</span>` : '',
        d2 ? `<span class="rule-chip rule-chip--dest">${d2}</span>` : '',
        rule.min_duration_sec != null
          ? `<span class="rule-chip rule-chip--dur">min ${rule.min_duration_sec}s</span>`
          : '',
        rule.max_duration_sec != null
          ? `<span class="rule-chip rule-chip--dur">max ${rule.max_duration_sec}s</span>`
          : '',
        rule.promo_possible
          ? `<span class="rule-chip rule-chip--promo">Promo</span>`
          : ''
      ]
        .filter(Boolean)
        .join('')

      return `
      <div class="rule-item" data-rule-id="${rule.id}">
        <div class="rule-item-info">
          <div class="rule-title">${
            rule.program_name || '(no program name)'
          }</div>
          <div class="rule-chips-row">${chips}</div>
        </div>
        <div class="d-flex gap-2 flex-shrink-0">
          <button class="btn btn-sm btn-outline-light" data-action="edit" data-id="${
            rule.id
          }">Edit</button>
          <button class="btn btn-sm btn-outline-danger" data-action="delete" data-id="${
            rule.id
          }" title="Alt+Click to delete">Delete</button>
        </div>
      </div>`
    })
    .join('')
}

formRule.addEventListener('submit', async event => {
  event.preventDefault()
  const payload = getRulePayload()

  if (!payload.program_name) {
    routeOutput.textContent = JSON.stringify(
      { error: 'program_name is required' },
      null,
      2
    )
    return
  }

  const id = fields.id.value.trim()
  const isUpdate = id.length > 0
  const response = await fetch(
    isUpdate ? `${apiUrl}/rules/${id}` : `${apiUrl}/rules`,
    {
      method: isUpdate ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }
  )
  const data = await response.json()
  routeOutput.textContent = JSON.stringify(data, null, 2)

  resetRuleForm()
  await loadRules(ruleSearch.value)
})

clearRuleBtn.addEventListener('click', () => {
  resetRuleForm()
})

ruleSearch.addEventListener('input', async () => {
  await loadRules(ruleSearch.value)
})

rulesList.addEventListener('click', async event => {
  const target = event.target
  if (!(target instanceof HTMLElement)) return

  const action = target.getAttribute('data-action')
  const id = target.getAttribute('data-id')
  if (!action || !id) return

  if (action === 'edit') {
    const response = await fetch(`${apiUrl}/rules/${id}`)
    const rule = await response.json()
    fillRuleForm(rule)
    routeOutput.textContent = JSON.stringify(rule, null, 2)
    return
  }

  if (action === 'delete') {
    if (!event.altKey) {
      routeOutput.textContent = 'Hold Alt and click Delete to confirm deletion.'
      return
    }
    const response = await fetch(`${apiUrl}/rules/${id}`, { method: 'DELETE' })
    const data = await response.json()
    routeOutput.textContent = JSON.stringify(data, null, 2)
    await loadRules(ruleSearch.value)
  }
})

setupChipGroup('destination_1_chips', 'destination_1')
setupChipGroup('destination_2_chips', 'destination_2')
resetRuleForm()
loadRules().catch(() => {
  routeOutput.textContent = JSON.stringify(
    { error: 'Unable to load rules from API.' },
    null,
    2
  )
})
