# Account Invoice Force Cancel

## 📋 Descrizione

Modulo Odoo 16 Enterprise Edition per la gestione avanzata della cancellazione di fatture validate in situazioni eccezionali. Questo modulo estende le funzionalità native di Odoo permettendo la cancellazione controllata e tracciata di documenti fiscali già registrati in contabilità.

## 🎯 Obiettivi dell'App

### Obiettivo Principale
Fornire agli amministratori di sistema uno strumento sicuro e tracciabile per rimuovere fatture validate erroneamente create, mantenendo la conformità normativa e l'audit trail completo.

### Obiettivi Specifici

#### 1. **Cancellazione Controllata**
- Aggiungere pulsante "Force Cancel" alle fatture in stato "Posted"
- Permettere il reset delle fatture a stato "Draft" per successiva cancellazione
- Rimozione completa dei movimenti contabili associati

#### 2. **Sicurezza e Controlli**
- Accesso limitato ai soli utenti con privilegi amministrativi
- Controlli preliminari prima della cancellazione:
  - Verifica stato SDI (blocco se già trasmessa)
  - Controllo presenza pagamenti collegati
  - Verifica riconciliazioni contabili esistenti

#### 3. **Tracciabilità e Audit**
- Log dettagliato di ogni operazione di cancellazione
- Registrazione automatica di:
  - Utente che ha eseguito l'operazione
  - Data e ora della cancellazione
  - Motivazione della rimozione
  - Backup dei dati originali

#### 4. **Conformità Normativa**
- Rispetto della normativa fiscale italiana
- Avvisi e disclaimer sui rischi legali
- Documentazione automatica per audit esterni
- Blocco operazioni su documenti con rilevanza fiscale

#### 5. **Usabilità**
- Interfaccia intuitiva con wizard di conferma
- Messaggi di warning chiari sui rischi
- Campo obbligatorio per motivazione della cancellazione
- Anteprima degli effetti della cancellazione

## 🔧 Funzionalità Tecniche

### Core Features
- **Force Cancel Button**: Pulsante dedicato nella vista fattura
- **Confirmation Wizard**: Dialog di conferma con campi obbligatori
- **Audit Log**: Tabella dedicata per tracciamento operazioni
- **Security Groups**: Gruppo di sicurezza dedicato per controllo accessi

### Controlli di Sicurezza
- **SDI Status Check**: Verifica stato trasmissione Fattura Elettronica
- **Payment Validation**: Controllo pagamenti associati
- **Reconciliation Check**: Verifica riconciliazioni esistenti
- **Accounting Period**: Controllo periodo contabile aperto/chiuso

### Logging e Backup
- **Operation History**: Storico completo delle cancellazioni
- **Data Backup**: Salvataggio automatico dati fattura prima della rimozione
- **Email Notifications**: Notifiche automatiche agli amministratori

## ⚠️ Avvertenze Legali

### Uso Responsabile
Questo modulo deve essere utilizzato esclusivamente per:
- Correzione di errori di sistema
- Rimozione di fatture di test finite in ambiente produzione  
- Situazioni eccezionali documentate e giustificate

### Rischi e Responsabilità
- **Conformità Fiscale**: L'utilizzo deve rispettare la normativa vigente
- **Audit Trail**: Mantenere documentazione completa delle operazioni
- **Responsabilità Utente**: L'amministratore si assume piena responsabilità dell'uso

## 🚀 Casi d'Uso Supportati

### Scenario 1: Fattura di Test in Produzione
- Fattura creata erroneamente in ambiente produzione
- Non ancora trasmessa allo SDI
- Necessità di rimozione completa per pulizia database

### Scenario 2: Errore di Sistema
- Duplicazione fatture per malfunzionamento
- Fatture con dati errati non correggibili
- Documenti creati da procedure automatiche difettose

### Scenario 3: Migrazione Dati
- Pulizia database dopo migrazione
- Rimozione documenti di test residui
- Standardizzazione numerazione fatture

## 📊 Requisiti Tecnici

- **Odoo Version**: 16.0 Enterprise Edition
- **Python**: 3.8+
- **Dipendenze**: account, base
- **Permessi Database**: Accesso completo per operazioni DDL/DML

## 🛡️ Sicurezza

### Gruppi di Accesso
- `group_invoice_force_cancel_admin`: Accesso completo alle funzionalità
- `group_invoice_force_cancel_view`: Solo visualizzazione audit log

### Audit e Compliance
- Registrazione completa delle operazioni
- Export dei log per audit esterni
- Integrazione con sistemi di backup esterni

## 📈 Roadmap Future

### Versione 1.1
- Integrazione con sistemi di backup esterni
- API REST per automazioni
- Dashboard di monitoraggio operazioni

### Versione 1.2  
- Integrazione con workflow di approvazione
- Notifiche avanzate multi-canale
- Plugin per sistemi di gestione documentale

---

**⚡ Importante**: Questo modulo è stato progettato per situazioni eccezionali. L'uso normale deve sempre seguire il flusso standard Odoo con note di credito per mantenere la tracciabilità fiscale completa.