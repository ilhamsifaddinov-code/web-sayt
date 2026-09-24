document.addEventListener("DOMContentLoaded", function () {
  if (window.lucide) window.lucide.createIcons();

  // ================= 1. DARK / LIGHT MODE =================
  const themeToggleBtn = document.getElementById('theme-toggle');
  const darkIcon = document.getElementById('theme-toggle-dark-icon');
  const lightIcon = document.getElementById('theme-toggle-light-icon');

  function updateThemeIcons() {
    if (document.documentElement.classList.contains('dark')) {
      if (darkIcon) darkIcon.classList.add('hidden');
      if (lightIcon) lightIcon.classList.remove('hidden');
    } else {
      if (darkIcon) darkIcon.classList.remove('hidden');
      if (lightIcon) lightIcon.classList.add('hidden');
    }
  }
  updateThemeIcons();

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function () {
      if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('color-theme', 'light');
      } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('color-theme', 'dark');
      }
      updateThemeIcons();
    });
  }

  // ================= 2. IPHONE STYLE NAV ANIMATION =================
  const nav = document.getElementById('desktop-nav');
  const indicator = document.getElementById('nav-indicator');
  const navItems = document.querySelectorAll('.nav-item');

  if (nav && indicator) {
    navItems.forEach(item => {
      item.addEventListener('mouseenter', (e) => {
        const rect = e.target.getBoundingClientRect();
        const navRect = nav.getBoundingClientRect();
        indicator.style.width = `${rect.width}px`;
        indicator.style.height = `${rect.height}px`;
        indicator.style.transform = `translate(${rect.left - navRect.left}px, ${rect.top - navRect.top}px)`;
        indicator.style.opacity = '1';
        
        // Change icon and text color to white securely
        e.target.classList.add('text-white');
        e.target.classList.remove('text-slate-600', 'dark:text-slate-200');
        const icon = e.target.querySelector('i');
        if (icon) {
            icon.setAttribute('data-original-color', icon.className);
            icon.className = 'w-4 h-4 text-white lucide';
        }
      });
      
      item.addEventListener('mouseleave', (e) => {
        indicator.style.opacity = '0';
        e.target.classList.remove('text-white');
        e.target.classList.add('text-slate-600', 'dark:text-slate-200');
        const icon = e.target.querySelector('i');
        if (icon && icon.hasAttribute('data-original-color')) {
            icon.className = icon.getAttribute('data-original-color');
        }
      });
    });
  }

  // ================= 3. TELEFON MASKASI (KOD + SAN) =================
  const countrySelect = document.getElementById('country_code');
  const phoneInput = document.getElementById('phone_number');

  if (countrySelect && phoneInput) {
    countrySelect.addEventListener('change', function() {
      phoneInput.value = '';
      phoneInput.focus();
    });

    phoneInput.addEventListener('input', function() {
      this.value = this.value.replace(/\D/g, ''); // Tek sanlar
      const maxLen = parseInt(countrySelect.options[countrySelect.selectedIndex].getAttribute('data-len'));
      if (this.value.length > maxLen) {
        this.value = this.value.substring(0, maxLen);
      }
    });

    // Form submission validation
    const form = phoneInput.closest('form');
    if (form) {
      form.addEventListener('submit', function(e) {
        const maxLen = parseInt(countrySelect.options[countrySelect.selectedIndex].getAttribute('data-len'));
        if (phoneInput.value.length !== maxLen) {
          e.preventDefault();
          const dict = translations[localStorage.getItem('site_lang') || 'qr'];
          alert(dict.alert_phone_len || `Telefon nomer ${maxLen} san bolıwı shárt!`);
          phoneInput.focus();
        }
      });
    }
  }

  // ================= 4. TOLÍQ TILLER (QR, UZ, RU, EN) =================
  const translations = {
    qr: {
      nav_specialists: "Qániygeler",
      nav_services: "Xızmetler",
      nav_reviews: "Pikirler",
      nav_chat: "Jeke Chat",
      nav_cabinet: "Kabinet",
      nav_login: "Kiriw",
      nav_register: "Dizimnen ótiw",
      mob_home: "Tiykarǵı",
      mob_specs: "Qániygeler",
      mob_cab: "Kabinet",
      mob_chat: "Chat",
      hero_badge: "Nókis qalasındaǵı professional logopedik oray",
      hero_title_1: "Balańız ",
      hero_title_accent: "anıq hám ráwan ",
      hero_title_2: "sóylewdi biz benen birge úyrensin!",
      hero_desc: "Sóylewi keshikken, háriplerdi anıq ayta almaytuǵın yamasa duduqlanatuǵın balalar ushın tájiriybeli qániygeler járdemi.",
      btn_book: "Qabılǵa jazılıw",
      btn_team: "Qániygeler menen tanısw",
      stat_happy: "500+ baxıtlı shańaraq",
      stat_desc: "Sóylew kemshiliklerinen qutıldı",
      issues_title: "Qaysı jaǵdaylarda logopedge barıw kerek?",
      issues_sub: "Eger balańızda tómendegi belgiler baqlansa, qániyge qabıllawın keshiktirmew zárúr:",
      iss_1_t: "3 jasta kesh gápiriw",
      iss_1_d: "Bala 3 jasqa shıqsa da tolıq sóylewdi baslamasa yamasa tek túsiniksiz dawıslar shıǵarsa.",
      iss_2_t: "Háriplerdi anıq ayta almaw",
      iss_2_d: "«R», «L», «Sh», «Ch» háriplerin buzıp yamasa basqa háripke almastırıp aytıw.",
      iss_3_t: "Duduqlanıw (Zaika)",
      iss_3_d: "Sóylew waqtında tınıstıń buzılıwı, dawıstıń qısılıwı yamasa sózlerdi qaytalap aytıw.",
      iss_4_t: "Sóz quramınıń kemligi",
      iss_4_d: "Óz pikirin erkin jetkerip bere almaw hám qatar-quralaslarına qaraǵanda sóz baylıǵınıń azlıǵı.",
      sec_specs_badge: "Biziń Topar",
      sec_specs_title: "Qániygeler",
      sec_specs_sub: "Hár bir qániygemiz kóp jıllıq tájiriybege hám joqarı nátiyjelilik kórsetkishine iye.",
      sp_rate: "Nátiyje",
      sp_price_label: "Qabıl bahası:",
      sp_book_btn: "Jazılıw",
      sec_serv_title: "Biziń Tiykarǵı Xızmetlerimiz",
      sec_serv_sub: "Bala menen jeke shınıǵıwlar zamanagóy pedagogikalıq metodika tiykarında ótiledi:",
      serv_1_t: "Dáslepki diagnostika",
      serv_1_d: "Balanıń sóylew apparatın tolıq tekseriw, unamlı hám qıyın táreplerin anıqlaw hám jeke dúzetiw rejesin dúziw.",
      serv_2_t: "Dawıslardı dúzetiw kursi",
      serv_2_d: "Ayırım qıyın háriplerdi durıs aytıw boyınsha arnawlı artikulyaciyalıq gimnastika hám sóylew refleksin bekkemlew.",
      serv_3_t: "Keshikken sóylewdi rawajlandırıw",
      serv_3_d: "3-5 jastaǵı balalarda tildi asıw, aktiv sóz baylıǵın kóbeytiw hám qızıqlı oyınlar arqalı qorqınıshtı jeńiw.",
      sec_rev_title: "Ata-analardıń Minnetdarshılıq Pikirleri",
      sec_rev_sub: "Biziń orayǵa isengen ata-analardıń nátiyjeleri hám haqıyqıy pikirleri:",
      rev_add_title: "Pikir qaldırıw",
      rev_placeholder: "Balańızdıń erisken nátiyjeleri haqqında óz pikirińizdi jazıp qaldırıń...",
      rev_rating_label: "Baha:",
      rev_send_btn: "Jiberiw",
      footer_desc: "Balańız anıq hám ráwan sóylewdi biz benen birge úyrensin. Nókis qalasındaǵı joqarı tájiriybeli qániygeler.",
      footer_addr_t: "Mánzil & Baylanıs",
      footer_addr: "Nókis qalası, Ernazar Alakóz kóshesi, 45-jay",
      footer_phone: "Telefon: +998 (90) 123-45-67",
      footer_work: "Is waqtı: 09:00 - 18:00 (Dem alıssız)",
      footer_quick_t: "Tezkor Siltemeler",
      footer_discount: "20% jeńillik penen dizimnen ótiw",
      footer_admin_chat: "Administratorǵa xat jazıw",
      footer_cabinet_link: "Jeke kabinetke kiriw",
      alert_phone_len: "Iltimas, telefon nomerdi tolıq kirgiziń!",
      reg_title: "Dizimnen Ótiw",
      reg_sub: "20% jeńillikke iye bolıń hám qániygelerge jazılıń",
      reg_name: "Atı-familiyańız:",
      reg_login: "Login (Username):",
      reg_phone: "Telefon nomerińiz:",
      reg_pass: "Parol jaratıń:",
      reg_btn: "Dizimnen ótiw",
      log_title: "Akkauntqa Kiriw",
      log_sub: "Jeke kabinet hám qabıllarǵa jazılıw ushın",
      log_btn: "Kiriw",
      log_no_acc: "Akkaunttıńız joq pa?",
      log_reg_link: "Dizimnen ótiw",
      dash_title: "Jeke Kabinet",
      dash_sub: "Bul jerde qániygelerge jazılasız hám rawajlanıw kártasın kóresiz.",
      dash_book_t: "Qániyge qabılına jazılıw",
      dash_book_s: "Qániygeni hám sáneni tańlań.",
      dash_cname: "Balanıń atı:",
      dash_cage: "Balanıń jası:",
      dash_sel_sp: "1. Qániygeni tańlań:",
      dash_sel_dt: "2. Sáneni tańlań:",
      dash_sel_tm: "3. Bos waqıttı tańlań:",
      dash_submit: "Tastıyıqlaw hám Jazılıw",
      dash_prog_t: "Balanıń rawajlanıw kártası",
      dash_prog_s: "Logoped tárepinen kiritilgen sabaq nátiyjeleri:",
      dash_my_apps: "Meniń qabıllarım",
      dash_sp_title: "Qániyge Kabineti",
      dash_sp_sub: "Sizge jazılǵan klientler hám rawajlanıw kártasına nátiyje jiberiw.",
      dash_sp_clients: "Maǵan jazılǵanlar (Klientler)",
      dash_sp_write: "Sabaq nátiyjesi hám Úyge tapsırma",
      admin_title: "Logoped Orayı Basqarıw Paneli",
      admin_sub: "Qabıllar, vrachlarǵa kabinet ashıw, bahalar hám parollar.",
      admin_u_count: "Dizimnen ótken adamlar",
      admin_a_count: "Aktiv Qabıllar",
      admin_s_count: "Barlıq Vrachlar",
      admin_tbl_t: "Barlıq Qabıllar Dizimi",
      admin_cred_t: "Foydalanıwshı & Vrach Parolların Ózgertiw",
      admin_cred_s: "Eski parol kórinbeydi, biraq jańa parol ornata alasız.",
      admin_cred_sel: "Adamdı tańlań:",
      admin_cred_btn: "Jańalaw",
      admin_sp_cab: "Vrachqa Jeke Kabinet Jaratıw",
      admin_sp_add: "Jańa Qániyge (Vrach) Qosıw",
      admin_sp_add_btn: "Qosıw",
      admin_sp_price: "Qabıl Bahaların Ózgertiw",
      admin_sp_mng: "Vrachlardı Basqarıw (Baha hám Óshiriw)",
      admin_sp_del: "Hákeket",
      admin_sp_save: "Saqlaw",
    },
    uz: {
      nav_specialists: "Mutaxassislar",
      nav_services: "Xizmatlar",
      nav_reviews: "Fikrlar",
      nav_chat: "Shaxsiy Chat",
      nav_cabinet: "Kabinet",
      nav_login: "Kirish",
      nav_register: "Ro'yxatdan o'tish",
      mob_home: "Asosiy",
      mob_specs: "Mutaxassislar",
      mob_cab: "Kabinet",
      mob_chat: "Chat",
      hero_badge: "Nukus shahridagi professional logopedik markaz",
      hero_title_1: "Farzandingiz ",
      hero_title_accent: "ravon va chiroyli ",
      hero_title_2: "gapirishni biz bilan o'rgansin!",
      hero_desc: "Nutqi kechikkan, harflarni to'g'ri ayta olmaydigan yoki duduqlanadigan bolalar uchun tajribali mutaxassislar yordami.",
      btn_book: "Qabulga yozilish",
      btn_team: "Mutaxassislar bilan tanishish",
      stat_happy: "500+ baxtli oila",
      stat_desc: "Nutq nuqsonlaridan xalos bo'ldi",
      issues_title: "Qaysi holatlarda logopedga murojaat qilish kerak?",
      issues_sub: "Agar farzandingizda quyidagi belgilar kuzatilsa, mutaxassis ko'rigini kechiktirmaslik lozim:",
      iss_1_t: "3 yoshda kech gapirish",
      iss_1_d: "Bola 3 yoshga to'lsa ham so'zlamasa yoki faqat tushunarsiz tovushlar chiqarsa.",
      iss_2_t: "Harflarni aniq ayta olmaslik",
      iss_2_d: "«R», «L», «Sh», «Ch» tovushlarini noto'g'ri talaffuz qilish.",
      iss_3_t: "Duduqlanish (Duduqlik)",
      iss_3_d: "Gapirish paytida nafas buzilishi, ovoz siqilishi yoki so'zlarni takrorlash.",
      iss_4_t: "So'z boyligining kamligi",
      iss_4_d: "O'z fikrini erkin ifodalay olmaslik va so'z boyligining yetishmasligi.",
      sec_specs_badge: "Bizning Jamoa",
      sec_specs_title: "Mutaxassislar",
      sec_specs_sub: "Har bir mutaxassisimiz ko'p yillik tajribaga ega.",
      sp_rate: "Natija",
      sp_price_label: "Qabul narxi:",
      sp_book_btn: "Yozilish",
      sec_serv_title: "Bizning Asosiy Xizmatlarimiz",
      sec_serv_sub: "Bola bilan yakka tartibdagi mashg'ulotlar o'tkaziladi:",
      serv_1_t: "Dastlabki diagnostika",
      serv_1_d: "Bolaning nutq apparatini to'liq tekshirish va reja tuzish.",
      serv_2_t: "Tovushlarni to'g'rilash",
      serv_2_d: "Qiyin talaffuz qilinadigan harflar bo'yicha maxsus mashqlar.",
      serv_3_t: "Nutqni rivojlantirish",
      serv_3_d: "3-5 yoshdagi bolalarda nutqni faollashtirish va so'z boyligini oshirish.",
      sec_rev_title: "Ota-onalarning Fikrlari",
      sec_rev_sub: "Markazimizga ishongan ota-onalarning samimiy fikrlari:",
      rev_add_title: "Fikr qoldirish",
      rev_placeholder: "Farzandingiz erishgan natijalar haqida yozing...",
      rev_rating_label: "Baho:",
      rev_send_btn: "Yuborish",
      footer_desc: "Farzandingiz ravon va chiroyli gapirishni o'rgansin. Nukusdagi tajribali mutaxassislar.",
      footer_addr_t: "Manzil & Aloqa",
      footer_addr: "Nukus shahri, Ernazar Olako'z ko'chasi, 45-uy",
      footer_phone: "Telefon: +998 (90) 123-45-67",
      footer_work: "Ish vaqti: 09:00 - 18:00",
      footer_quick_t: "Tezkor Havolalar",
      footer_discount: "20% chegirma bilan ro'yxatdan o'tish",
      footer_admin_chat: "Administratorga yozish",
      footer_cabinet_link: "Shaxsiy kabinetga kirish",
      alert_phone_len: "Iltimos, telefon raqamni to'liq kiriting!",
      reg_title: "Ro'yxatdan O'tish",
      reg_sub: "20% chegirmaga ega bo'ling",
      reg_name: "Ism-familiyangiz:",
      reg_login: "Login (Username):",
      reg_phone: "Telefon raqamingiz:",
      reg_pass: "Parol yarating:",
      reg_btn: "Ro'yxatdan o'tish",
      log_title: "Akkauntga Kirish",
      log_sub: "Shaxsiy kabinet va qabullar uchun",
      log_btn: "Kirish",
      log_no_acc: "Akkauntingiz yo'qmi?",
      log_reg_link: "Ro'yxatdan o'tish",
      dash_title: "Shaxsiy Kabinet",
      dash_sub: "Mutaxassislarga yozilish va rivojlanish xaritasi.",
      dash_book_t: "Qabulga yozilish",
      dash_book_s: "Mutaxassis va sanani tanlang.",
      dash_cname: "Bolaning ismi:",
      dash_cage: "Bolaning yoshi:",
      dash_sel_sp: "1. Mutaxassisni tanlang:",
      dash_sel_dt: "2. Sanani tanlang:",
      dash_sel_tm: "3. Bo'sh vaqtni tanlang:",
      dash_submit: "Tasdiqlash va Yozilish",
      dash_prog_t: "Rivojlanish xaritasi",
      dash_prog_s: "Logoped tomonidan kiritilgan natijalar:",
      dash_my_apps: "Mening qabullarim",
      dash_sp_title: "Mutaxassis Kabineti",
      dash_sp_sub: "Mijozlar va natijalar kiritish.",
      dash_sp_clients: "Menga yozilganlar",
      dash_sp_write: "Natija va Vazifa yozish",
      admin_title: "Logoped Markazi Boshqaruvi",
      admin_sub: "Barcha ma'lumotlarni boshqarish.",
      admin_u_count: "Ro'yxatdan o'tganlar",
      admin_a_count: "Faol Qabullar",
      admin_s_count: "Barcha Vrachlar",
      admin_tbl_t: "Barcha Qabullar Ro'yxati",
      admin_cred_t: "Foydalanuvchi & Vrach Parollarini O'zgartirish",
      admin_cred_s: "Eski parol yashirilgan, lekin yangi parol ornatishingiz mumkin.",
      admin_cred_sel: "Odamni tanlang:",
      admin_cred_btn: "Yangilash",
      admin_sp_cab: "Vrachga Kabinet Ochish",
      admin_sp_add: "Yangi Vrach Qo'shish",
      admin_sp_add_btn: "Qo'shish",
      admin_sp_price: "Narxlarni O'zgartirish",
      admin_sp_mng: "Vrachlarni Boshqarish",
      admin_sp_del: "Harakat",
      admin_sp_save: "Saqlash",
    },
    ru: {
      nav_specialists: "Специалисты",
      nav_services: "Услуги",
      nav_reviews: "Отзывы",
      nav_chat: "Личный Чат",
      nav_cabinet: "Кабинет",
      nav_login: "Войти",
      nav_register: "Регистрация",
      mob_home: "Главная",
      mob_specs: "Врачи",
      mob_cab: "Кабинет",
      mob_chat: "Чат",
      hero_badge: "Профессиональный логопедический центр в Нукусе",
      hero_title_1: "Пусть ваш ребенок ",
      hero_title_accent: "четко и красиво ",
      hero_title_2: "говорит вместе с нами!",
      hero_desc: "Помощь опытных логопедов для детей с задержкой речи и дефектами звукопроизношения.",
      btn_book: "Записаться на прием",
      btn_team: "Познакомиться с врачами",
      stat_happy: "500+ счастливых семей",
      stat_desc: "Избавились от дефектов речи",
      issues_title: "Когда стоит обратиться к логопеду?",
      issues_sub: "Если у вашего ребенка наблюдаются следующие признаки:",
      iss_1_t: "Задержка речи в 3 года",
      iss_1_d: "Ребенок в 3 года не говорит фразами или произносит невнятные звуки.",
      iss_2_t: "Нечеткое произношение",
      iss_2_d: "Искажение или замена звуков «Р», «Л», «Ш», «Ч».",
      iss_3_t: "Заикание",
      iss_3_d: "Заминки, повторение слогов или затрудненное дыхание.",
      iss_4_t: "Бедный словарный запас",
      iss_4_d: "Трудности в формулировании мыслей.",
      sec_specs_badge: "Наша Команда",
      sec_specs_title: "Специалисты",
      sec_specs_sub: "Каждый наш специалист обладает многолетним опытом.",
      sp_rate: "Успех",
      sp_price_label: "Цена приема:",
      sp_book_btn: "Записаться",
      sec_serv_title: "Наши Услуги",
      sec_serv_sub: "Индивидуальные занятия с детьми:",
      serv_1_t: "Диагностика",
      serv_1_d: "Обследование речевого аппарата ребенка.",
      serv_2_t: "Коррекция звуков",
      serv_2_d: "Артикуляционная гимнастика и автоматизация звуков.",
      serv_3_t: "Развитие речи",
      serv_3_d: "Стимуляция речевой активности у детей от 3 лет.",
      sec_rev_title: "Отзывы Родителей",
      sec_rev_sub: "Реальные отзывы родителей нашего центра:",
      rev_add_title: "Оставить отзыв",
      rev_placeholder: "Расскажите об успехах вашего ребенка...",
      rev_rating_label: "Оценка:",
      rev_send_btn: "Отправить",
      footer_desc: "Опытные логопеды в Нукусе.",
      footer_addr_t: "Адрес & Контакты",
      footer_addr: "г. Нукус, ул. Ерназар Алакоз, 45",
      footer_phone: "Телефон: +998 (90) 123-45-67",
      footer_work: "Режим: 09:00 - 18:00",
      footer_quick_t: "Ссылки",
      footer_discount: "Регистрация со скидкой 20%",
      footer_admin_chat: "Связаться с администратором",
      footer_cabinet_link: "Войти в личный кабинет",
      alert_phone_len: "Пожалуйста, введите полный номер телефона!",
      reg_title: "Регистрация",
      reg_sub: "Получите скидку 20%",
      reg_name: "Имя Фамилия:",
      reg_login: "Логин (Username):",
      reg_phone: "Ваш телефон:",
      reg_pass: "Придумайте пароль:",
      reg_btn: "Зарегистрироваться",
      log_title: "Вход в аккаунт",
      log_sub: "Для записи и личного кабинета",
      log_btn: "Войти",
      log_no_acc: "Нет аккаунта?",
      log_reg_link: "Регистрация",
      dash_title: "Личный Кабинет",
      dash_sub: "Запись к специалистам и карта развития.",
      dash_book_t: "Записаться на прием",
      dash_book_s: "Выберите врача и дату.",
      dash_cname: "Имя ребенка:",
      dash_cage: "Возраст ребенка:",
      dash_sel_sp: "1. Выберите врача:",
      dash_sel_dt: "2. Выберите дату:",
      dash_sel_tm: "3. Выберите время:",
      dash_submit: "Подтвердить",
      dash_prog_t: "Карта развития",
      dash_prog_s: "Результаты от логопеда:",
      dash_my_apps: "Мои записи",
      dash_sp_title: "Кабинет Врача",
      dash_sp_sub: "Мои клиенты и результаты.",
      dash_sp_clients: "Записи ко мне",
      dash_sp_write: "Добавить результат",
      admin_title: "Панель Администратора",
      admin_sub: "Управление записями, врачами и пользователями.",
      admin_u_count: "Пользователей",
      admin_a_count: "Активные Записи",
      admin_s_count: "Все Врачи",
      admin_tbl_t: "Список Записей",
      admin_cred_t: "Изменить Пароли Пользователей и Врачей",
      admin_cred_s: "Из соображений безопасности старый пароль скрыт, но вы можете задать новый.",
      admin_cred_sel: "Выберите пользователя:",
      admin_cred_btn: "Обновить",
      admin_sp_cab: "Создать Кабинет Врачу",
      admin_sp_add: "Добавить Врача",
      admin_sp_add_btn: "Добавить",
      admin_sp_price: "Изменить Цены",
      admin_sp_mng: "Управление Врачами",
      admin_sp_del: "Действие",
      admin_sp_save: "Сохранить",
    },
    en: {
      nav_specialists: "Specialists",
      nav_services: "Services",
      nav_reviews: "Reviews",
      nav_chat: "Direct Chat",
      nav_cabinet: "Dashboard",
      nav_login: "Sign In",
      nav_register: "Sign Up",
      mob_home: "Home",
      mob_specs: "Doctors",
      mob_cab: "Cabinet",
      mob_chat: "Chat",
      hero_badge: "Professional Speech Therapy Center in Nukus",
      hero_title_1: "Help your child ",
      hero_title_accent: "speak clearly and fluently ",
      hero_title_2: "with our expert team!",
      hero_desc: "Professional assistance from certified speech therapists for children with speech delays and stuttering.",
      btn_book: "Book Appointment",
      btn_team: "Meet Specialists",
      stat_happy: "500+ Happy Families",
      stat_desc: "Achieved fluent speech",
      issues_title: "When should you consult a speech therapist?",
      issues_sub: "If you notice any of the following signs in your child:",
      iss_1_t: "Speech delay at age 3",
      iss_1_d: "The child does not use complete sentences at 3 years old.",
      iss_2_t: "Difficulty pronouncing",
      iss_2_d: "Distorting or substituting difficult sounds like 'R', 'L'.",
      iss_3_t: "Stuttering",
      iss_3_d: "Involuntary repetitions of syllables or blocks.",
      iss_4_t: "Limited vocabulary",
      iss_4_d: "Struggles to express thoughts and falls behind peers.",
      sec_specs_badge: "Our Team",
      sec_specs_title: "Specialists",
      sec_specs_sub: "Each of our speech therapists has years of clinical experience.",
      sp_rate: "Success",
      sp_price_label: "Session Fee:",
      sp_book_btn: "Book Now",
      sec_serv_title: "Our Services",
      sec_serv_sub: "One-on-one sessions tailored to each child:",
      serv_1_t: "Diagnosis",
      serv_1_d: "Comprehensive assessment of the speech organs.",
      serv_2_t: "Sound Articulation",
      serv_2_d: "Specialized oral motor gymnastics.",
      serv_3_t: "Speech Activation",
      serv_3_d: "Stimulating active speech in children aged 3-5.",
      sec_rev_title: "Parent Testimonials",
      sec_rev_sub: "Genuine feedback from parents who trusted our clinic:",
      rev_add_title: "Leave a Review",
      rev_placeholder: "Share your child's achievements...",
      rev_rating_label: "Rating:",
      rev_send_btn: "Submit",
      footer_desc: "Empower your child to speak fluently. Trusted specialists in Nukus.",
      footer_addr_t: "Address & Contact",
      footer_addr: "Nukus city, Ernazar Alakoz str, 45",
      footer_phone: "Phone: +998 (90) 123-45-67",
      footer_work: "Hours: 09:00 - 18:00",
      footer_quick_t: "Quick Links",
      footer_discount: "Sign up with 20% discount",
      footer_admin_chat: "Message Administrator",
      footer_cabinet_link: "Open Dashboard",
      alert_phone_len: "Please enter the full phone number!",
      reg_title: "Registration",
      reg_sub: "Get a 20% discount",
      reg_name: "Full Name:",
      reg_login: "Username:",
      reg_phone: "Phone Number:",
      reg_pass: "Create Password:",
      reg_btn: "Sign Up",
      log_title: "Account Login",
      log_sub: "Access dashboard and appointments",
      log_btn: "Sign In",
      log_no_acc: "No account?",
      log_reg_link: "Sign Up",
      dash_title: "Personal Dashboard",
      dash_sub: "Book specialists and track progress.",
      dash_book_t: "Book Appointment",
      dash_book_s: "Select doctor and date.",
      dash_cname: "Child's Name:",
      dash_cage: "Child's Age:",
      dash_sel_sp: "1. Select Doctor:",
      dash_sel_dt: "2. Select Date:",
      dash_sel_tm: "3. Select Time:",
      dash_submit: "Confirm Booking",
      dash_prog_t: "Development Map",
      dash_prog_s: "Results from therapist:",
      dash_my_apps: "My Appointments",
      dash_sp_title: "Doctor Dashboard",
      dash_sp_sub: "Clients and lesson notes.",
      dash_sp_clients: "My Appointments",
      dash_sp_write: "Add Result & Homework",
      admin_title: "Admin Control Panel",
      admin_sub: "Manage appointments, users, and doctors.",
      admin_u_count: "Registered Users",
      admin_a_count: "Active Appointments",
      admin_s_count: "Total Doctors",
      admin_tbl_t: "All Appointments",
      admin_cred_t: "Change User & Doctor Passwords",
      admin_cred_s: "Passwords are hidden for security, but you can assign a new one.",
      admin_cred_sel: "Select User:",
      admin_cred_btn: "Update",
      admin_sp_cab: "Create Doctor Account",
      admin_sp_add: "Add New Doctor",
      admin_sp_add_btn: "Add",
      admin_sp_price: "Update Prices",
      admin_sp_mng: "Manage Doctors",
      admin_sp_del: "Action",
      admin_sp_save: "Save",
    }
  };

  function setLanguage(lang) {
    localStorage.setItem('site_lang', lang);
    const dict = translations[lang] || translations['qr'];

    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) el.innerText = dict[key];
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (dict[key]) el.setAttribute('placeholder', dict[key]);
    });

    const menu = document.getElementById('lang-dropdown-menu');
    if (menu) menu.classList.add('hidden');
  }

  const globeTrigger = document.getElementById('globe-trigger-btn');
  const langDropdown = document.getElementById('lang-dropdown-menu');

  if (globeTrigger && langDropdown) {
    globeTrigger.addEventListener('click', function (e) {
      e.stopPropagation();
      langDropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', function (e) {
      if (!globeTrigger.contains(e.target) && !langDropdown.contains(e.target)) {
        langDropdown.classList.add('hidden');
      }
    });
  }

  document.querySelectorAll('.lang-option-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      setLanguage(this.getAttribute('data-lang'));
    });
  });

  setLanguage(localStorage.getItem('site_lang') || 'qr');
});
