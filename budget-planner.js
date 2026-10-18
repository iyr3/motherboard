const usageNames = {
  office: 'أوفيس واستخدام يومي',
  study: 'دراسة ومحاضرات',
  programming: 'برمجة وتطوير',
  gaming1080: 'ألعاب 1080p',
  gaming1440: 'ألعاب 1440p',
  creation: 'مونتاج وتصميم'
};

const builds = [
  {
    id: 'refurb-office', price: 9500, range: '8,000–12,000 ج.م', name: 'مكتبي اقتصادي مجدد',
    uses: ['office', 'study'], target: 'أوفيس، تصفح، اجتماعات ومحاضرات أونلاين',
    summary: 'كمبيوتر مكتبي من فئة الشركات بعد التجديد. أقل تكلفة عملية للمهام الأساسية، دون كرت شاشة منفصل.',
    parts: [['المعالج', 'Core i5 جيل 8 أو مكافئ'], ['اللوحة', 'لوحة الشركة الأصلية'], ['الذاكرة', '16GB DDR4'], ['الرسوميات', 'Intel UHD مدمجة'], ['التخزين', 'SSD SATA 256GB'], ['مزود الطاقة', 'OEM أصلي مع الجهاز'], ['الكيسة', 'كيسة مكتبية مجددة']],
    performance: 'مناسب للمتصفح، Office، الفيديو والاجتماعات. لا يناسب الألعاب الحديثة أو المونتاج الثقيل.',
    platform: 'خيار مستعمل مجدد؛ افحص صحة SSD والحرارة والضمان قبل الدفع.',
    limits: 'سعة التخزين والترقية محدودة مقارنة بكيسة جديدة، ولا توجد بطاقة ألعاب منفصلة.',
    upgrade: 'أضف SSD أكبر أو RAM متوافقة. لا تركب GPU قبل التأكد من الطاقة والمساحة.',
    condition: 'مستعمل مجدد · افحص الضمان والحالة', power: 'استهلاك منخفض'
  },
  {
    id: 'refurb-study', price: 14500, range: '12,000–17,000 ج.م', name: 'دراسة واستخدام يومي مريح',
    uses: ['office', 'study', 'programming'], target: 'الدراسة، البرمجة التعليمية، وتعدد مهام متوسط',
    summary: 'معالج حديث نسبيًا ببطاقة رسومية مدمجة وذاكرة ثنائية القناة؛ خيار متوازن دون شراء GPU.',
    parts: [['المعالج', 'Ryzen 5 4600G أو مكافئ'], ['اللوحة', 'A520M بعد فحص BIOS'], ['الذاكرة', '16GB DDR4 (2×8GB)'], ['الرسوميات', 'Radeon مدمجة'], ['التخزين', 'NVMe 500GB'], ['مزود الطاقة', '500–550W موثوق'], ['الكيسة', 'Micro-ATX جيدة التهوية']],
    performance: 'سريع في البرامج اليومية وبيئات البرمجة. مناسب لألعاب خفيفة أو قديمة بإعدادات منخفضة.',
    platform: 'منصة AM4 وذاكرة DDR4؛ راجع دعم المعالج على موديل اللوحة المحدد.',
    limits: 'الرسوميات المدمجة تشارك RAM ولا تعوض كرت شاشة للألعاب الثقيلة.',
    upgrade: 'يمكن إضافة بطاقة منفصلة لاحقًا إذا كان مزود الطاقة والكيسة يسمحان بذلك.',
    condition: 'أسعار القطع الجديدة والمستعملة تختلف؛ تحقق من الضمان', power: 'منخفض إلى متوسط'
  },
  {
    id: 'apu-home', price: 19500, range: '17,000–23,000 ج.م', name: 'جهاز منزلي قابل للتطوير',
    uses: ['office', 'study', 'programming'], target: 'استخدام منزلي، دراسة وبرمجة مع تعدد مهام أفضل',
    summary: 'رسوميات مدمجة أقوى وذاكرة 32GB تمنح الجهاز عمرًا أطول من تجميعة الحد الأدنى.',
    parts: [['المعالج', 'Ryzen 5 5600G'], ['اللوحة', 'A520M أو B550M'], ['الذاكرة', '32GB DDR4 (2×16GB)'], ['الرسوميات', 'Radeon مدمجة'], ['التخزين', 'NVMe 1TB'], ['مزود الطاقة', '550W موثوق'], ['الكيسة', 'Micro-ATX مع مروحتين']],
    performance: 'ممتاز للتصفح والدراسة والبرمجة اليومية، وألعاب إلكترونية خفيفة بدقة منخفضة إلى 1080p.',
    platform: 'منصة AM4؛ تأكد من تحديث BIOS إذا كانت اللوحة قديمة المخزون.',
    limits: 'ليست بديلًا عن GPU منفصل للألعاب الجديدة ذات المتطلبات العالية.',
    upgrade: 'أضف بطاقة ألعاب لاحقًا، واحتفظ بمزود طاقة يدعم استهلاكها المتوقع.',
    condition: 'تجميعة اقتصادية؛ قارن أسعار القطع والضمان', power: 'متوسط'
  },
  {
    id: 'entry-gaming-used', price: 29500, range: '25,000–34,000 ج.م', name: 'أقل بداية للألعاب المنفصلة',
    uses: ['gaming1080', 'study', 'programming'], target: 'ألعاب 1080p مع بطاقة مستعملة مفحوصة',
    summary: 'معالج بست أنوية وبطاقة RX 6600 مستعملة بحالة جيدة؛ قيمة قوية إذا كان السعر والفحص مناسبين.',
    parts: [['المعالج', 'Ryzen 5 5500 أو 5600 حسب العرض'], ['اللوحة', 'A520M أو B550M'], ['الذاكرة', '16GB DDR4 (2×8GB)'], ['الرسوميات', 'RX 6600 مستعملة ومختبرة'], ['التخزين', 'NVMe 500GB'], ['مزود الطاقة', '650W موثوق جديد'], ['الكيسة', 'Micro-ATX بتدفق هواء']],
    performance: 'ألعاب كثيرة بدقة 1080p بإعدادات متوسطة أو مرتفعة حسب اللعبة. الأداء يختلف كثيرًا بين العناوين.',
    platform: 'خليط محتمل من قطع جديدة ومستعملة؛ اختبر البطاقة تحت الضغط وافحص الحرارة والمراوح.',
    limits: 'لا يوجد ضمان موحد للبطاقة المستعملة، وقد تحتاج RAM أو SSD للترقية قريبًا.',
    upgrade: 'ابدأ بـ32GB RAM و1TB SSD؛ لا تستخدم مزود طاقة مجهولًا مع بطاقة مستعملة.',
    condition: 'البطاقة مستعملة: اطلب اختبارًا وفاتورة أو ضمانًا متبقيًا', power: 'متوسط'
  },
  {
    id: 'gaming-1080-new', price: 42000, range: '36,000–49,000 ج.م', name: 'ألعاب 1080p بقطع جديدة',
    uses: ['gaming1080', 'study', 'programming'], target: 'ألعاب 1080p بإعدادات مرتفعة وتجربة مستقرة',
    summary: 'بطاقة جديدة بضمان وذاكرة 32GB وتخزين واسع؛ لمن يريد الابتعاد عن مخاطرة المستعمل.',
    parts: [['المعالج', 'Ryzen 5 5600'], ['اللوحة', 'B550M'], ['الذاكرة', '32GB DDR4 (2×16GB)'], ['الرسوميات', 'RX 7600 أو أداء مكافئ'], ['التخزين', 'NVMe 1TB'], ['مزود الطاقة', '650W موثوق بضمان'], ['الكيسة', 'Micro-ATX بواجهة Mesh']],
    performance: 'مناسبة لألعاب 1080p الحديثة. ارفع أو اخفض إعدادات الظلال وتتبع الأشعة حسب اللعبة.',
    platform: 'منصة AM4 ناضجة وتكلفتها الإجمالية أقل؛ خيار جيد إذا لم تكن الترقية إلى AM5 أولوية.',
    limits: 'مسار الترقية أقصر من منصة AM5، وقدرة 1440p تعتمد على اللعبة والبطاقة المختارة.',
    upgrade: 'يمكن نقل التخزين أو البطاقة إلى جهاز لاحق، مع مراجعة توافق مزود الطاقة.',
    condition: 'استهدف قطعًا جديدة بضمان واضح', power: 'متوسط إلى مرتفع'
  },
  {
    id: 'balanced-am5', price: 58500, range: '50,000–68,000 ج.م', name: 'منصة حديثة قابلة للترقية',
    uses: ['gaming1080', 'gaming1440', 'programming', 'creation'], target: 'ألعاب 1080p قوية و1440p متوسطة وبرامج إنتاجية',
    summary: 'منصة AM5 أحدث مع DDR5؛ توازن بين الأداء الحالي وإمكانية ترقية المعالج مستقبلًا.',
    parts: [['المعالج', 'Ryzen 5 7600'], ['اللوحة', 'B650M مع VRM مناسب'], ['الذاكرة', '32GB DDR5 (2×16GB)'], ['الرسوميات', 'RX 7600 أو فئة قريبة'], ['التخزين', 'NVMe 1TB'], ['مزود الطاقة', '650–750W حسب البطاقة'], ['الكيسة', 'Micro-ATX/ATX بتهوية جيدة']],
    performance: 'تجربة قوية في 1080p ومناسبة للبدء في 1440p مع ضبط الإعدادات حسب اللعبة.',
    platform: 'AM5 وDDR5؛ تحقق من إصدار BIOS وقائمة دعم المعالج والذاكرة.',
    limits: 'سعر المنصة أعلى من AM4، وقد تتجاوز البطاقة وحدها سقف التجميعة إذا ارتفعت أسعارها.',
    upgrade: 'ترقية GPU أو المعالج لاحقًا دون استبدال الذاكرة واللوحة مباشرة.',
    condition: 'تجميعة جديدة؛ قارن قيمة الضمان لكل قطعة', power: 'متوسط إلى مرتفع'
  },
  {
    id: 'gaming-1440', price: 78000, range: '67,000–90,000 ج.م', name: 'ألعاب 1440p متوازنة',
    uses: ['gaming1440', 'gaming1080', 'creation'], target: 'ألعاب 1440p بجودة أعلى وتحرير محتوى متوسط',
    summary: 'بطاقة بذاكرة كبيرة ومنصة قابلة للترقية؛ اختر طراز GPU وفق الألعاب والأسعار المتاحة.',
    parts: [['المعالج', 'Ryzen 5 7600'], ['اللوحة', 'B650M أو B650 ATX'], ['الذاكرة', '32GB DDR5 (2×16GB)'], ['الرسوميات', 'RX 7800 XT أو أداء قريب'], ['التخزين', 'NVMe 1TB'], ['مزود الطاقة', '750W موثوق حسب موديل GPU'], ['الكيسة', 'ATX/Micro-ATX واسعة التهوية']],
    performance: 'تستهدف 1440p؛ الأداء ومعدل الإطارات يتغيران باختلاف اللعبة وإعدادات الجودة.',
    platform: 'AM5 وDDR5، مع مساحة جيدة للترقيات اللاحقة.',
    limits: 'تأكد من طول البطاقة ووصلات الطاقة، ولا تعتمد على اسم الفئة وحده.',
    upgrade: 'يمكن إضافة مساحة تخزين أو ترقية GPU بعد عدة سنوات مع إبقاء المنصة.',
    condition: 'جديدة بضمان؛ راجع أبعاد البطاقة قبل شراء الكيسة', power: 'مرتفع'
  },
  {
    id: 'high-end-gaming', price: 115000, range: '98,000–132,000 ج.م', name: 'ألعاب قوية وإنتاج محتوى',
    uses: ['gaming1440', 'creation', 'programming'], target: 'ألعاب 1440p عالية الأداء وبعض تجارب 4K وتصيير GPU',
    summary: 'GPU قوية ومعالج ألعاب ممتاز، مع طاقة وتبريد مناسبين للاستخدام الطويل.',
    parts: [['المعالج', 'Ryzen 7 7800X3D'], ['اللوحة', 'B650 ATX بمنافذ مناسبة'], ['الذاكرة', '32GB DDR5 6000 تقريبًا'], ['الرسوميات', 'RTX 4070 Ti SUPER أو مكافئ سعري'], ['التخزين', 'NVMe 2TB'], ['مزود الطاقة', '850W موثوق وفق توصية البطاقة'], ['الكيسة', 'ATX بتدفق هواء ومساحة GPU']],
    performance: 'تجربة قوية في 1440p؛ 4K ممكنة في ألعاب كثيرة بعد موازنة إعدادات الرسوم.',
    platform: 'AM5 وDDR5 مع مجال ترقية وذاكرة إضافية عند الحاجة.',
    limits: 'التكلفة العالية لا تعني أن الشاشة أو التبريد يمكن إهمالهما.',
    upgrade: 'للعمل الإبداعي، ارفع RAM إلى 64GB إذا كانت مشاريعك تستهلك ذاكرة كبيرة.',
    condition: 'فئة مرتفعة؛ اطلب ضمانًا محليًا لكل القطع', power: 'مرتفع جدًا'
  },
  {
    id: 'creator-workstation', price: 145000, range: '128,000–165,000 ج.م', name: 'محطة عمل لصناعة المحتوى',
    uses: ['creation', 'programming'], target: 'مونتاج طويل، مشاريع تصميم كبيرة، وبناء وبرامج متعددة',
    summary: 'ذاكرة 64GB ومعالج متعدد الأنوية وتخزين واسع؛ بطاقة الرسوميات تتغير حسب برامج العمل.',
    parts: [['المعالج', 'Ryzen 9 7900 أو فئة متعددة الأنوية'], ['اللوحة', 'B650 ATX مع منافذ M.2 إضافية'], ['الذاكرة', '64GB DDR5 (2×32GB)'], ['الرسوميات', 'RTX 4070 SUPER أو مكافئ'], ['التخزين', 'NVMe 2TB + مساحة أرشيف اختيارية'], ['مزود الطاقة', '850W موثوق'], ['التبريد', 'مبرد مناسب للحمل الطويل']],
    performance: 'مناسبة للمشاريع المتوسطة والكبيرة؛ سرعة التصدير تعتمد على البرنامج والترميز والـ GPU.',
    platform: 'اختر قطعًا مدعومة رسميًا من البرنامج الذي تستخدمه، خصوصًا في الرندر وتسريع الفيديو.',
    limits: 'قد تكون مبالغة للألعاب فقط؛ 64GB لا تفيد إذا كان استخدامك خفيفًا.',
    upgrade: 'يمكن زيادة RAM والتخزين بعد مراقبة استهلاك المشاريع الفعلي.',
    condition: 'محطة عمل؛ راجع توافق البرامج والضمان قبل اعتماد القطع', power: 'مرتفع'
  }
];

const slider = document.getElementById('budgetSlider');
const numberInput = document.getElementById('budgetNumber');
const usageSelect = document.getElementById('usageSelect');
const formatMoney = value => `${new Intl.NumberFormat('ar-EG', { maximumFractionDigits: 0 }).format(value)} ج.م`;

function buildCard(build, index, recommended, budget) {
  const overBudget = build.price > budget;
  return `<article class="budget-card ${recommended ? 'recommended' : ''} ${overBudget ? 'out-of-budget' : ''}" data-build="${index}">
    <div class="budget-card-head"><div><span class="guide-tag">${overBudget ? 'الخيار التالي' : `ضمن ميزانيتك · ${index + 1}`} / ${build.range}</span><h3>${build.name}</h3><p>${build.target}</p></div><div class="budget-price">حوالي ${formatMoney(build.price)}</div></div>
    <p class="budget-summary">${build.summary}</p>
    <div class="budget-parts">${build.parts.map(([label, value]) => `<div class="budget-part"><small>${label}</small><strong>${value}</strong></div>`).join('')}</div>
    <div class="budget-performance"><div><small>الأداء المتوقع</small><p>${build.performance}</p></div><div><small>المنصة والتوافق</small><p>${build.platform}</p></div><div><small>حالة الشراء / الطاقة</small><p>${build.condition}<br>استهلاك: ${build.power}</p></div></div>
    <div class="budget-reason"><p><strong>نقاط الانتباه</strong><br>${build.limits}</p><p><strong>ترقية مقترحة</strong><br>${build.upgrade}</p></div>
    ${overBudget ? `<p class="budget-gap">تحتاج زيادة نحو ${formatMoney(build.price - budget)} للوصول إلى هذه الخطة.</p>` : ''}
  </article>`;
}

function renderBudgets() {
  const budget = Number(slider.value);
  const usage = usageSelect.value;
  const matching = builds.filter(build => build.uses.includes(usage));
  const affordable = matching.filter(build => build.price <= budget);
  const recommended = affordable.at(-1) || matching[0];
  const nextBuild = affordable.length ? matching.find(build => build.price > budget) : null;
  const visibleBuilds = affordable.length
    ? [...affordable, ...(nextBuild ? [nextBuild] : [])]
    : matching.slice(0, 1);

  document.getElementById('budgetOutput').textContent = formatMoney(budget);
  numberInput.value = budget;
  document.querySelectorAll('[data-budget]').forEach(button => {
    button.classList.toggle('active', Number(button.dataset.budget) === budget);
  });

  document.getElementById('recommendationLabel').textContent = affordable.length
    ? `أفضل اختيار لـ${usageNames[usage]} ضمن ميزانيتك`
    : `ميزانيتك أقل من أقل خطة لـ${usageNames[usage]}`;
  document.getElementById('recommendationTitle').textContent = recommended.name;
  document.getElementById('recommendationDescription').textContent = affordable.length
    ? `${recommended.target} ${recommended.summary}`
    : `أقل خيار مناسب يبدأ من ${formatMoney(recommended.price)}؛ ينقص ميزانيتك ${formatMoney(recommended.price - budget)}.`;
  document.getElementById('recommendationPrice').textContent = formatMoney(recommended.price);
  document.getElementById('budgetResultsMeta').textContent = affordable.length
    ? `${affordable.length} تجميعة مناسبة لاستخدامك وضمن ميزانيتك. أظهرنا الخطة التالية للمقارنة عند توفرها.`
    : `لا توجد خطة كاملة لهذا الاستخدام ضمن السقف الحالي. هذه أقل خطة مناسبة لتعرف القطع المطلوبة والفارق.`;
  document.getElementById('budgetList').innerHTML = visibleBuilds.length
    ? visibleBuilds.map(build => buildCard(build, builds.indexOf(build), build === recommended && affordable.length > 0, budget)).join('')
    : '<div class="empty-state">لا توجد خطة مناسبة لهذا الاستخدام.</div>';
}

slider.addEventListener('input', renderBudgets);
numberInput.addEventListener('change', () => {
  const value = Math.max(Number(slider.min), Math.min(Number(slider.max), Number(numberInput.value) || Number(slider.min)));
  slider.value = Math.round(value / 1000) * 1000;
  renderBudgets();
});
usageSelect.addEventListener('change', renderBudgets);
document.querySelectorAll('[data-budget]').forEach(button => button.addEventListener('click', () => {
  slider.value = button.dataset.budget;
  renderBudgets();
}));
renderBudgets();
