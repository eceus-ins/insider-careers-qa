# insider-careers-qa

## Test metrics: MySQL + Grafana

UI test sonuçları (`insider_automation_tests`) her pytest çalışmasında `test_results_db` (MySQL) veritabanına loglanır — build başına bir `build_runs` satırı, test başına bir `test_runs` satırı (durum, süre, hata mesajı). Grafana bu veritabanına bağlanıp pass rate / execution time dashboard'unu gösterir.

### Kurulum

```bash
cd infra
cp .env.example .env   # şifreleri kendine göre doldur
docker compose up -d
```

Bu, `localhost:3307` üzerinde MySQL ve `localhost:3000` üzerinde Grafana'yı ayağa kaldırır. Datasource ve "QA Test Metrics" dashboard'u otomatik provision edilir (`infra/grafana/provisioning/`) — Grafana UI'dan elle kurulum gerekmez.

### Testleri DB'ye loglayarak çalıştırma

```bash
cd insider_automation_tests
pip install -r requirements.txt
DB_HOST=localhost DB_PORT=3307 DB_USER=test_user DB_PASSWORD=<infra/.env'deki MYSQL_PASSWORD> \
  pytest --browser=chrome --headless
```

CI/CD tarafında bu adım `Jenkinsfile` üzerinden otomatik çalışır (Jenkins credential store'da `mysql-test-password` adında bir credential eklemen gerekir). GitHub Actions workflow'u (`.github/workflows/ui-tests.yml`) testleri bulutta çalıştırmaya devam eder ama bulut runner'ı yerel Docker ağına erişemediği için DB'ye yazmaz — DB loglama sorumluluğu Jenkins'te.

### Dashboard

`http://localhost:3000/d/qa-test-metrics` — Pass Rate %, toplam fail sayısı, pass/fail/skip dağılımı, günlük test trendi, ortalama/en yavaş test süreleri, en çok fail eden testler.