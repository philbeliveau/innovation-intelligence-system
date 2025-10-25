# Mapping Vidéos Newcode → Innovation Intelligence System

**Branche:** `architecture-cleanup-prisma`
**Repo:** https://github.com/philbeliveau/innovation-intelligence-system

---

## 🎯 Résumé Exécutif

Le repo **innovation-intelligence-system** (branche `architecture-cleanup-prisma`) est une **application full-stack moderne COMPLÈTE** avec TOUS les composants nécessaires pour 18 sujets vidéo sur 20.

### **Stack Complète Confirmée:**

**Frontend (`innovation-web/`):**
- ✅ Next.js 15.5.6 + React 19.1.0 (App Router)
- ✅ TypeScript strict mode
- ✅ Tailwind CSS 4 + shadcn/ui components
- ✅ Clerk Auth (@clerk/nextjs ^6.33.7)
- ✅ Prisma Client (@prisma/client ^6.18.0)
- ✅ LangChain (@langchain/openai ^1.0.0)
- ✅ Vercel Blob (@vercel/blob ^2.0.0)
- ✅ Jest + Testing Library (tests configurés)
- ✅ Dark mode (next-themes)

**Backend (`backend/`):**
- ✅ FastAPI 0.115.0 + Uvicorn
- ✅ LangChain 0.1.20 pipeline (preserved from original)
- ✅ OpenAI integration
- ✅ PDF processing (pypdf)
- ✅ Docker + Dockerfile ready
- ✅ pytest + pytest-asyncio configured
- ✅ Railway deployment docs

**Database (Prisma Schema):**
- ✅ PostgreSQL via Prisma
- ✅ Models:
  - `User` (Clerk integration via clerkId)
  - `Document` (file uploads with Vercel Blob URLs)
  - `PipelineRun` (innovation analysis tracking)
  - `OpportunityCard` (generated innovation cards)
  - `InspirationReport` (full reports)
  - `StageOutput` (pipeline stage outputs)
- ✅ Migrations ready
- ✅ Seed scripts (tsx prisma/seed.ts)

**Deployment Infrastructure:**
- ✅ Vercel deployment guide (`innovation-web/VERCEL-DEPLOYMENT.md`)
- ✅ Railway deployment guide (`backend/DEPLOYMENT.md`)
- ✅ Prisma deployment guide (`innovation-web/PRISMA-SETUP.md`)
- ✅ Environment variables documented

**Manquant (facilement ajoutables):**
- ❌ Stripe integration (paiements) - Effort: 2-3h
- ⚠️ Railway database provisionné (nécessite compte Railway)

---

## 📹 Mapping Détaillé: 20 Sujets Vidéo

### ✅ **APPLICABLES IMMÉDIATEMENT** (16 sujets)

---

#### **Sujet 1: FastAPI MCP - Debugger son application**

**Statut:** ✅ **EXCELLENT MATCH**

**Ce qu'il y a:**
- Backend FastAPI complet dans `backend/app/`
- Endpoints API pour pipeline, documents, users
- Pipeline LangChain multi-stages intégré

**Application:**
Debugger le backend FastAPI qui traite des documents et génère des innovations via LangChain.

**Démo (2-3 min):**
1. **[0:00-0:30]** Montrer l'app qui tourne: backend FastAPI + frontend Next.js
2. **[0:30-1:00]** Problème: endpoint `/api/pipeline/run` retourne erreur 500
3. **[1:00-1:45]** Ouvrir Claude Code avec FastAPI MCP:
   - "Qu'est-ce qui ne va pas avec /api/pipeline/run?"
   - Claude inspecte endpoint, teste requête, lit logs
4. **[1:45-2:15]** Claude identifie: validation Pydantic manquante sur `companyName`
5. **[2:15-2:45]** Fix appliqué, re-test via FastAPI MCP → ✅ fonctionne
6. **[2:45-3:00]** Commentaire: "Debugger FastAPI sans quitter Claude"

**Fichiers concernés:**
- `backend/app/main.py` - FastAPI application
- `backend/app/routes/` - API routes (pipeline, documents, users)
- `backend/pipeline/` - LangChain pipeline stages

---

#### **Sujet 2: Serena MCP - Économiser des tokens intelligemment**

**Statut:** ✅ **PARFAIT MATCH**

**Ce qu'il y a:**
- Pipeline LangChain avec multiples appels LLM (5 stages)
- Prompts volumineux dans `backend/pipeline/prompts/`
- Documentation research massive (24 docs, 60K+ mots)

**Application:**
Optimiser les appels LLM du pipeline d'analyse innovation pour réduire coûts de 40-60%.

**Démo (2-3 min):**
1. **[0:00-0:30]** Lancer analyse innovation SANS Serena:
   - Upload PDF → Pipeline 5 stages → Afficher token count total
   - Exemple: "45,000 tokens consommés"
2. **[0:30-1:00]** Activer Serena MCP dans Claude Code
3. **[1:00-1:45]** Relancer même analyse AVEC Serena:
   - Serena optimise contexte envoyé à chaque stage
   - Résume docs research au lieu de tout envoyer
4. **[1:45-2:15]** Résultat: "18,000 tokens consommés" (60% économie)
5. **[2:15-2:45]** Comparaison qualité: outputs identiques
6. **[2:45-3:00]** Calcul ROI: "$450/mois → $180/mois"

**Fichiers concernés:**
- `backend/pipeline/stages/` - 5 pipeline stages (chacun appelle LLM)
- `backend/pipeline/prompts/` - Prompt templates
- `documentation/` - Research docs (context à optimiser)

---

#### **Sujet 3: Vercel & Railway MCP - Déployer sans être DevOps**

**Statut:** ✅ **DEPLOYMENT READY**

**Ce qu'il y a:**
- `innovation-web/VERCEL-DEPLOYMENT.md` (guide complet)
- `backend/DEPLOYMENT.md` (Railway + Docker)
- `innovation-web/PRISMA-SETUP.md` (database setup)
- Dockerfile prêt dans `backend/`

**Application:**
Déployer l'app innovation complète (frontend + backend + DB) en moins de 5 minutes.

**Démo (4-5 min):**
1. **[0:00-0:30]** App tourne en local: localhost:3000 (frontend) + localhost:8000 (backend)
2. **[0:30-1:15]** Claude Code + Vercel MCP: "Déploie mon frontend"
   - Détecte Next.js 15
   - Configure build automatiquement
   - Deploy → URL: `innovation-app.vercel.app`
3. **[1:15-2:30]** Claude Code + Railway MCP: "Déploie mon backend FastAPI"
   - Crée service Railway
   - Configure Dockerfile
   - Provisionne PostgreSQL database
   - Variables d'environnement (OpenAI API key, DATABASE_URL)
   - Deploy → URL: `backend-production-xyz.up.railway.app`
4. **[2:30-3:15]** Connecter frontend ↔ backend:
   - Update `NEXT_PUBLIC_API_URL` dans Vercel
   - Redeploy frontend
5. **[3:15-4:00]** Test complet:
   - Upload PDF sur app live
   - Backend traite via LangChain
   - Affiche résultats
6. **[4:00-4:30]** Prisma migration sur Railway DB:
   - `npx prisma migrate deploy`
   - Database tables créées
7. **[4:30-5:00]** Commentaire: "De localhost à production en 5 minutes"

**Fichiers concernés:**
- `innovation-web/VERCEL-DEPLOYMENT.md`
- `backend/DEPLOYMENT.md`
- `backend/Dockerfile`
- `innovation-web/prisma/schema.prisma`

---

#### **Sujet 4: Playwright MCP - Tester automatiquement**

**Statut:** ✅ **APPLICATION TESTABLE**

**Ce qu'il y a:**
- Frontend Next.js avec UI complète
- Flow utilisateur: Login (Clerk) → Upload PDF → View Results
- Components testables (`innovation-web/components/`)

**Application:**
Tester automatiquement le workflow complet d'analyse innovation avec Playwright.

**Démo (3-4 min):**
1. **[0:00-0:30]** Montrer le flow utilisateur manuellement:
   - Connexion Clerk
   - Upload PDF "savannah-bananas.pdf"
   - Wait for analysis (5 stages)
   - View opportunity cards
2. **[0:30-1:15]** Dans Claude: "Teste ce flow automatiquement avec Playwright"
3. **[1:15-2:30]** Claude via Playwright MCP:
   - Lance navigateur (visible)
   - Navigue vers app
   - Clerk auto-login (test user)
   - Upload file via dropzone
   - Wait for progress indicator (5 stages)
   - Vérifie que 5-7 opportunity cards apparaissent
4. **[2:30-3:00]** Screenshot de chaque étape sauvegardé
5. **[3:00-3:30]** Introduire bug: supprimer bouton upload
6. **[3:30-4:00]** Re-run test → Échec, Claude identifie où
7. **[4:00-4:20]** Commentaire: "Testing E2E sans écrire de code"

**Fichiers concernés:**
- `innovation-web/app/` - Pages Next.js
- `innovation-web/components/` - UI components (upload, cards, etc.)
- `innovation-web/middleware.ts` - Clerk auth middleware

---

#### **Sujet 5: Sub-agents - Déléguer la lecture, garder le contrôle**

**Statut:** ✅ **EXCELLENT MATCH**

**Ce qu'il y a:**
- Documentation massive: 24 research docs (60K+ mots)
- Research domains: `research/`, `psychology/`, `agent-personas/`, `workflow-design/`
- Pipeline complexe nécessitant contexte research

**Application:**
Sub-agent lit toute la documentation research, résume pour l'agent principal qui implémente feature.

**Démo (3-4 min):**
1. **[0:00-0:45]** Tâche: "Ajoute un 6e stage au pipeline basé sur biomimicry research"
2. **[0:45-1:15]** **Mauvaise approche** (sans sub-agent):
   - Agent principal lit tous les docs research
   - Token count: 55,000 tokens
   - Perd le fil, résultat médiocre
3. **[1:15-2:00]** **Bonne approche** (avec sub-agent):
   - "Lance un sub-agent pour analyser la documentation biomimicry"
4. **[2:00-3:00]** Sub-agent:
   - Lit `research/sit-systematic-inventive-thinking.md`
   - Lit `agent-personas/nature-translator.md`
   - Analyse patterns biomimicry
   - Produit résumé 2 pages: "Voici comment intégrer biomimicry au pipeline"
5. **[3:00-3:45]** Agent principal:
   - Reçoit résumé concis (2K tokens)
   - Implémente nouveau stage basé sur résumé
   - Code précis, bien structuré
6. **[3:45-4:15]** Comparaison:
   - Sans sub-agent: 55K tokens, résultat moyen
   - Avec sub-agent: 8K tokens total, résultat excellent
7. **[4:15-4:30]** Commentaire: "Délégation = efficacité"

**Fichiers concernés:**
- `research/` (9 docs: TRIZ, SIT, biomimicry, neuroscience)
- `psychology/` (4 docs: SPECTRE framework, validation)
- `agent-personas/` (7 docs: 6 agent personalities)
- `backend/pipeline/stages/` (à étendre avec nouveau stage)

---

#### **Sujet 6: Loop & Vérification - Développer des systèmes robustes**

**Statut:** ✅ **PARFAIT CANDIDAT**

**Ce qu'il y a:**
- Pipeline 5 stages séquentiels
- Validation framework SPECTRE défini dans research
- Tests pytest configurés (`backend/pytest.ini`)

**Application:**
Ajouter boucles de vérification après chaque stage du pipeline pour maintenir qualité.

**Démo (4-5 min):**
1. **[0:00-0:45]** **Sans vérification** (approach actuelle):
   - Pipeline run complet
   - Stage 3 génère output de mauvaise qualité
   - Stages 4-5 construisent sur mauvaises bases
   - Résultat final: médiocre
2. **[0:45-1:30]** Ajouter loop verification au Stage 1:
   - "Implémente verification loop pour Stage 1"
   - Claude ajoute:
     ```python
     # Stage 1: Pattern Recognition
     output = run_stage_1(input)

     # Verification loop
     quality_score = verify_output(output, quality_criteria)
     if quality_score < 0.8:
         output = correct_and_retry(output, feedback)
     ```
3. **[1:30-2:30]** Définir critères de qualité:
   - Output doit contenir 5-7 patterns minimum
   - Chaque pattern doit avoir score de confiance >0.7
   - Format YAML valide
4. **[2:30-3:30]** Appliquer à tous les 5 stages:
   - Stage 2: Validation SPECTRE framework
   - Stage 3: Market psychology check
   - Stage 4: Technical feasibility
   - Stage 5: Final synthesis quality
5. **[3:30-4:15]** Re-run pipeline avec verification loops:
   - Stage 3 échoue verification
   - Claude corrige automatiquement
   - Re-vérifie → passe
   - Stages 4-5 construisent sur bonnes bases
6. **[4:15-4:45]** Résultat: Quality score 9.2/10 vs 6.5/10
7. **[4:45-5:00]** Commentaire: "Plus lent maintenant, plus rapide sur le long terme"

**Fichiers concernés:**
- `backend/pipeline/stages/stage_1_pattern_recognition.py`
- `backend/pipeline/stages/stage_2_validation.py`
- `backend/pipeline/stages/stage_3_market_analysis.py`
- `backend/pipeline/stages/stage_4_technical_feasibility.py`
- `backend/pipeline/stages/stage_5_synthesis.py`
- `psychology/spectre-validation-framework.md`
- `backend/tests/` (ajouter tests de verification)

---

#### **Sujet 7: La Stack Moderne - Vue d'ensemble**

**Statut:** ✅ **STACK COMPLÈTE DÉJÀ EN PLACE**

**Ce qu'il y a:**
- ✅ Vercel (frontend Next.js)
- ✅ Railway (backend FastAPI + PostgreSQL)
- ✅ Prisma (ORM + migrations)
- ✅ Clerk (auth)
- ✅ NeonDB compatible (PostgreSQL)
- ❌ Stripe (à ajouter - 2h effort)

**Application:**
Présenter la stack complète et montrer comment chaque pièce s'intègre.

**Démo (5-6 min):**
1. **[0:00-1:00]** Vue d'ensemble - Diagramme de la stack:
   ```
   [User Browser]
        ↓
   [Vercel - Next.js Frontend]
        ↓ (Auth)
   [Clerk Authentication]
        ↓ (API calls)
   [Railway - FastAPI Backend]
        ↓ (ORM)
   [Prisma Client]
        ↓ (SQL)
   [Railway PostgreSQL Database]
   ```

2. **[1:00-2:00]** **Layer 1: Database (Prisma + Railway PostgreSQL)**
   - Montrer schema.prisma
   - Run migration: `npx prisma migrate dev`
   - Open Prisma Studio: visualiser tables
   - Insert seed data

3. **[2:00-3:15]** **Layer 2: Backend (FastAPI + Railway)**
   - Montrer endpoints API (`backend/app/routes/`)
   - Test endpoint: `POST /api/pipeline/run`
   - Backend query DB via Prisma
   - Process document via LangChain
   - Return results

4. **[3:15-4:30]** **Layer 3: Frontend (Next.js + Vercel)**
   - Montrer pages (`innovation-web/app/`)
   - Upload component calls backend API
   - Results affichés via shadcn/ui components
   - Dark mode toggle (next-themes)

5. **[4:30-5:15]** **Layer 4: Auth (Clerk)**
   - Montrer middleware.ts (protected routes)
   - Login flow: Clerk modal
   - User sync Clerk → Prisma DB
   - User documents & pipeline runs

6. **[5:15-5:45]** **Layer 5: Storage (Vercel Blob)**
   - Upload PDF → Vercel Blob
   - Get signed URL
   - Backend download from Blob URL
   - Process avec LangChain

7. **[5:45-6:00]** Commentaire: "Stack moderne, assemblée et fonctionnelle"

**Fichiers concernés:**
- `innovation-web/prisma/schema.prisma`
- `backend/app/main.py`
- `innovation-web/app/` (pages)
- `innovation-web/middleware.ts` (Clerk)
- `innovation-web/app/api/upload/route.ts` (Vercel Blob)

---

#### **Sujet 8: Prisma MCP - Créer et migrer des bases de données**

**Statut:** ✅ **PRISMA FULLY CONFIGURED**

**Ce qu'il y a:**
- Schema Prisma complet (6 models)
- Migrations configured
- Seed script ready (`prisma/seed.ts`)
- Railway PostgreSQL integration docs

**Application:**
Montrer comment créer et modifier le schéma DB, migrer, et visualiser avec Prisma Studio.

**Démo (4-5 min):**
1. **[0:00-0:30]** Partir de schema existant (6 models)
2. **[0:30-1:15]** Besoin: "J'ai besoin d'ajouter un système de favoris pour les OpportunityCards"
3. **[1:15-2:00]** Claude + Prisma MCP:
   - Analyse schema actuel
   - Propose modification:
     ```prisma
     model OpportunityCard {
       // ... existing fields
       isStarred Boolean @default(false)  // NOUVEAU

       @@index([isStarred])  // NOUVEAU index
     }
     ```
4. **[2:00-2:30]** Créer migration:
   - Claude: `npx prisma migrate dev --name add-starred-cards`
   - Migration SQL générée automatiquement
5. **[2:30-3:00]** Appliquer sur Railway:
   - Claude: `npx prisma migrate deploy`
   - Database mise à jour sans downtime
6. **[3:00-3:45]** Ouvrir Prisma Studio:
   - `npx prisma studio`
   - Visualiser OpportunityCards table
   - Voir nouveau champ `isStarred`
   - Modifier données visuellement
7. **[3:45-4:15]** Ajouter données via seed:
   - Modifier `prisma/seed.ts`
   - `npm run prisma:seed`
   - 50 opportunity cards créées avec isStarred randomisé
8. **[4:15-4:45]** Utiliser dans app:
   - Frontend: ajouter star icon
   - API route: toggle isStarred
   - Query: `where: { isStarred: true }`
9. **[4:45-5:00]** Commentaire: "De l'idée de données à la feature complète en 5 minutes"

**Fichiers concernés:**
- `innovation-web/prisma/schema.prisma`
- `innovation-web/prisma/migrations/`
- `innovation-web/prisma/seed.ts`
- `innovation-web/PRISMA-SETUP.md`

---

#### **Sujet 9: Context7 MCP - Documentation toujours à jour**

**Statut:** ✅ **APPLICABLE**

**Ce qu'il y a:**
- Next.js 15.5.6 (version très récente)
- React 19.1.0 (version cutting-edge)
- Prisma 6.18.0 (dernière version)
- LangChain 1.0+ (API changée)

**Application:**
Utiliser Context7 pour accéder docs officielles latest versions lors de l'ajout de features.

**Démo (3-4 min):**
1. **[0:00-0:30]** Besoin: "Utilise les nouveaux React 19 hooks (use, useActionState)"
2. **[0:30-1:00]** **Sans Context7:**
   - Chercher Google "react 19 hooks"
   - Trouver article de 2023 (React 18)
   - Code ne fonctionne pas (API changée)
3. **[1:00-1:45]** **Avec Context7:**
   - Activer Context7 MCP
   - "Utilise React 19 use hook pour data fetching"
   - Context7 → docs React 19 officielles
4. **[1:45-2:30]** Claude génère code correct:
   ```tsx
   import { use } from 'react';

   function Component({ dataPromise }) {
     const data = use(dataPromise);  // React 19 feature
     return <div>{data}</div>;
   }
   ```
5. **[2:30-3:00]** Autre exemple: "Utilise Next.js 15 partial prerendering"
6. **[3:00-3:30]** Context7 → Next.js 15 docs
7. **[3:30-3:50]** Code généré avec config correcte
8. **[3:50-4:00]** Commentaire: "Toujours la dernière doc, zéro friction"

**Fichiers concernés:**
- `innovation-web/package.json` (dépendances latest)
- `innovation-web/app/` (pages avec features modernes)
- `innovation-web/next.config.ts`

---

#### **Sujet 10: GitHub MCP - Code review automatisé**

**Statut:** ✅ **REPO GITHUB ACTIF**

**Ce qu'il y a:**
- Repo GitHub public
- Branche `architecture-cleanup-prisma` active
- Code Python + TypeScript à reviewer

**Application:**
Review automatique d'un commit qui ajoute une feature au pipeline.

**Démo (4-5 min):**
1. **[0:00-0:30]** Commit récent: "Add Stage 6 - Strategic Foresight"
2. **[0:30-1:00]** Dans Claude: "Review mon dernier commit via GitHub"
3. **[1:00-2:15]** Claude via GitHub MCP:
   - Fetch commit diff
   - Analyse changements:
     - Nouveau fichier: `backend/pipeline/stages/stage_6_foresight.py`
     - Modifié: `backend/app/routes/pipeline.py`
     - Modifié: `innovation-web/prisma/schema.prisma`
4. **[2:15-3:15]** Feedback détaillé:
   - ✅ Good: Stage suit pattern des autres stages
   - ⚠️ Warning: Manque tests pour nouveau stage
   - ❌ Issue: Schema Prisma manque migration
   - 💡 Suggestion: Ajouter rate limiting (OpenAI API)
   - 🔒 Security: API key exposée dans code (move to .env)
5. **[3:15-4:00]** "Crée une PR avec tes corrections"
6. **[4:00-4:30]** Claude:
   - Crée branche `fix/stage-6-improvements`
   - Applique corrections
   - Ajoute tests pytest
   - Crée migration Prisma
   - Move API key to .env
   - Ouvre PR avec description détaillée
7. **[4:30-5:00]** Montrer PR sur GitHub: propre, testée, sécurisée
8. **[5:00-5:15]** Commentaire: "Review de niveau senior, automatisé"

**Fichiers concernés:**
- `backend/pipeline/stages/`
- `backend/tests/`
- `innovation-web/prisma/`

---

#### **Sujet 11: Clerk MCP - Authentication en 10 minutes**

**Statut:** ✅ **CLERK DÉJÀ INTÉGRÉ**

**Ce qu'il y a:**
- Clerk v6.33.7 configuré
- Middleware protection (`innovation-web/middleware.ts`)
- User sync Clerk ↔ Prisma
- Protected routes

**Application:**
Montrer comment Clerk est configuré et comment ajouter protection à nouvelle route.

**Démo (3-4 min):**
1. **[0:00-0:30]** App actuelle: login via Clerk fonctionne
2. **[0:30-1:00]** Montrer middleware.ts:
   ```ts
   export default clerkMiddleware((auth, req) => {
     if (isProtectedRoute(req)) auth.protect();
   });
   ```
3. **[1:00-1:45]** Créer nouvelle page: `/innovation-web/app/admin/page.tsx`
4. **[1:45-2:15]** "Protège cette page admin avec Clerk"
5. **[2:15-2:45]** Claude ajoute:
   ```ts
   // middleware.ts
   const protectedRoutes = [
     '/dashboard',
     '/upload',
     '/admin'  // NOUVEAU
   ];
   ```
6. **[2:45-3:15]** Test:
   - Naviguer vers /admin sans login → Redirect vers Clerk
   - Login → Accès granted
7. **[3:15-3:45]** Bonus: User role-based access
   - "Limite /admin aux users avec role='admin'"
   - Claude ajoute check sur `session.user.role`
8. **[3:45-4:00]** Commentaire: "Sécurité production-grade en minutes"

**Fichiers concernés:**
- `innovation-web/middleware.ts`
- `innovation-web/app/layout.tsx` (ClerkProvider)
- `innovation-web/lib/auth.ts`

---

#### **Sujet 14: Custom Instructions - Agent personnalisé**

**Statut:** ✅ **CLAUDE.MD DÉJÀ COMPLET**

**Ce qu'il y a:**
- `CLAUDE.md` racine du repo (22KB)
- `innovation-web/CLAUDE.md` (6KB)
- Context complet sur le projet

**Application:**
Montrer comment CLAUDE.md configure Claude pour connaître le projet.

**Démo (2-3 min):**
1. **[0:00-0:30]** Problème: nouveau dev joint le projet, ne connaît rien
2. **[0:30-1:00]** Sans CLAUDE.md:
   - "Ajoute un endpoint API"
   - Claude génère code generic, pas adapté au projet
3. **[1:00-1:45]** Avec CLAUDE.md:
   - Claude lit automatiquement CLAUDE.md au démarrage
   - Comprend:
     - Stack: Next.js 15 + FastAPI + Prisma + Clerk
     - Architecture: innovation pipeline 5 stages
     - Conventions: TypeScript strict, Prisma ORM
     - BMAD framework integration
4. **[1:45-2:15]** "Ajoute un endpoint API pour exporter results en PDF"
5. **[2:15-2:45]** Claude génère code parfaitement adapté:
   - FastAPI route dans bon dossier
   - Utilise Prisma pour query
   - Suit conventions projet
   - Ajoute auth Clerk check
   - Génère PDF avec jsPDF (déjà dans package.json)
6. **[2:45-3:00]** Commentaire: "Claude connaît VOTRE projet"

**Fichiers concernés:**
- `CLAUDE.md` (racine)
- `innovation-web/CLAUDE.md`

---

#### **Sujet 15: Memory & Context Management - Projets complexes**

**Statut:** ✅ **PROJET COMPLEXE IDÉAL**

**Ce qu'il y a:**
- Monorepo avec frontend + backend
- 24 research docs
- Multiple systèmes (auth, DB, pipeline, storage)

**Application:**
Créer structure `.context/` pour documenter décisions architecturales.

**Démo (4-5 min):**
1. **[0:00-0:45]** Projet complexe: Claude se perd après 10 conversations
2. **[0:45-1:30]** "Crée une structure .context/ pour documenter décisions"
3. **[1:30-2:30]** Claude crée:
   ```
   .context/
     decisions/
       ADR-001-why-clerk-over-nextauth.md
       ADR-002-why-fastapi-not-nextjs-api.md
       ADR-003-prisma-over-raw-sql.md
       ADR-004-langchain-version-pinned.md
     architecture/
       system-overview.md
       data-flow-diagram.md
       deployment-architecture.md
     conventions/
       code-style.md
       commit-messages.md
       api-patterns.md
   ```
4. **[2:30-3:15]** Documenter ADR-001:
   ```markdown
   # ADR-001: Why Clerk over NextAuth

   Date: 2024-01-15
   Status: Accepted

   ## Context
   Need authentication for innovation app with user management.

   ## Decision
   Use Clerk instead of NextAuth.

   ## Rationale
   - Built-in user management UI
   - Easier webhook integration
   - Better TypeScript support
   - Less code to maintain

   ## Consequences
   - Paid service ($25/mo)
   - Vendor lock-in (mitigated by standard OAuth)
   - Faster development
   ```
5. **[3:15-4:00]** 3 semaines plus tard:
   - "Pourquoi on utilise Clerk?"
   - Claude lit `.context/decisions/ADR-001-*.md`
   - Répond avec contexte exact
6. **[4:00-4:30]** "Devrait-on migrer vers NextAuth?"
7. **[4:30-4:50]** Claude analyse ADR, répond avec raisons documentées
8. **[4:50-5:00]** Commentaire: "Mémoire persistante = projets scalables"

**Fichiers à créer:**
- `.context/` structure complète

---

#### **Sujet 16: Diagnostic Brownfield - Documenter projet existant**

**Statut:** ✅ **PROJET PARFAIT POUR DIAGNOSTIC**

**Ce qu'il y a:**
- Projet existant complexe
- Architecture multi-tier
- Multiple technologies

**Application:**
Analyst agent documente le projet complet pour nouveau dev.

**Démo (5-6 min):**
1. **[0:00-0:30]** Nouveau dev arrive, projet mystère
2. **[0:30-1:00]** Activer `/BMad:agents:analyst`
3. **[1:00-1:30]** Analyst: `*document-project`
4. **[1:30-3:30]** Agent analyse:
   - Scan `innovation-web/` → Next.js 15, Clerk, Prisma
   - Scan `backend/` → FastAPI, LangChain pipeline
   - Scan `prisma/schema.prisma` → 6 models, relations
   - Scan research docs → Innovation intelligence domain
   - Scan deployment docs → Vercel + Railway

5. **[3:30-5:00]** Génère rapport structuré:
   ```markdown
   # Innovation Intelligence System - Project Analysis

   ## Tech Stack
   - Frontend: Next.js 15.5.6 + React 19 + TypeScript
   - Backend: FastAPI 0.115.0 + Python 3.10+
   - Database: PostgreSQL via Prisma 6.18.0
   - Auth: Clerk 6.33.7
   - Storage: Vercel Blob
   - AI: LangChain 1.0 + OpenAI

   ## Architecture
   - Monorepo structure (frontend + backend)
   - 5-stage innovation pipeline
   - User uploads documents → Pipeline analyzes → Generates opportunity cards

   ## Database Schema
   - User (Clerk sync)
   - Document (uploaded PDFs)
   - PipelineRun (analysis sessions)
   - OpportunityCard (generated innovations)
   - InspirationReport (full reports)

   ## Key Workflows
   1. User uploads PDF via Vercel Blob
   2. Backend fetches from Blob URL
   3. LangChain pipeline (5 stages)
   4. Results saved to PostgreSQL
   5. Frontend displays opportunity cards

   ## Technical Debt
   - ⚠️ No Stripe integration (payments needed)
   - ⚠️ Limited error handling in pipeline
   - ⚠️ No retry logic for LLM failures

   ## Deployment
   - Frontend: Vercel
   - Backend: Railway + PostgreSQL
   - Environment: 15+ env variables
   ```

6. **[5:00-5:45]** "Comment j'ajoute un nouveau pipeline stage?"
7. **[5:45-6:00]** Analyst utilise diagnostic, donne plan précis

**Fichiers concernés:**
- Tout le repo (scan complet)
- Output: `docs/project-diagnostic.md`

---

#### **Sujet 17: TDD - Tests avant code**

**Statut:** ✅ **TESTS CONFIGURÉS**

**Ce qu'il y a:**
- Jest configuré (`innovation-web/jest.config.js`)
- pytest configuré (`backend/pytest.ini`)
- Testing Library installed

**Application:**
Ajouter une feature avec TDD: tests d'abord, code ensuite.

**Démo (5-6 min):**
1. **[0:00-0:30]** Feature: "Système de tags pour OpportunityCards"
2. **[0:30-1:30]** **Phase RED** - Écrire tests d'abord:
   - "Claude, écris les tests pour le système de tags"
   - Tests backend (pytest):
     ```python
     def test_add_tag_to_card():
         card = create_opportunity_card()
         result = add_tag(card.id, "biomimicry")
         assert "biomimicry" in result.tags

     def test_filter_cards_by_tag():
         cards = filter_by_tag("TRIZ")
         assert all("TRIZ" in c.tags for c in cards)
     ```
   - Tests frontend (Jest):
     ```tsx
     it('displays tags on card', () => {
       render(<OpportunityCard tags={['biomimicry', 'TRIZ']} />)
       expect(screen.getByText('biomimicry')).toBeInTheDocument()
     })
     ```

3. **[1:30-2:00]** Run tests: ❌ TOUS échouent (normal, pas de code encore)

4. **[2:00-3:30]** **Phase GREEN** - Implémenter code:
   - Modifier Prisma schema:
     ```prisma
     model OpportunityCard {
       // ... existing
       tags String[]  // NOUVEAU
     }
     ```
   - Migration: `npx prisma migrate dev`
   - Backend API:
     ```python
     @router.post("/{card_id}/tags")
     async def add_tag(card_id: str, tag: str):
         card = await db.opportunitycard.update(
             where={"id": card_id},
             data={"tags": {"push": tag}}
         )
         return card
     ```
   - Frontend component:
     ```tsx
     <div className="tags">
       {tags.map(tag => <Badge key={tag}>{tag}</Badge>)}
     </div>
     ```

5. **[3:30-4:00]** Re-run tests: ✅ TOUS passent

6. **[4:00-5:00]** **Phase REFACTOR**:
   - "Optimise le code sans casser tests"
   - Claude refactorise:
     - Extrait TagBadge component
     - Ajoute index DB sur tags
     - Cache tag queries
   - Re-run tests: ✅ toujours passent

7. **[5:00-5:45]** Ajouter edge cases:
   - Test: duplicate tags
   - Test: empty tag string
   - Claude ajout validation

8. **[5:45-6:00]** Commentaire: "TDD = confiance que ça marche"

**Fichiers concernés:**
- `innovation-web/__tests__/`
- `backend/tests/`
- `innovation-web/prisma/schema.prisma`
- `backend/app/routes/cards.py`
- `innovation-web/components/opportunity-card.tsx`

---

#### **Sujet 18: Refactoring automatisé - Dette technique**

**Statut:** ✅ **CODE À REFACTORER PRÉSENT**

**Ce qu'il y a:**
- Pipeline code complexe
- Some legacy patterns
- Opportunities for improvement

**Application:**
Refactorer code pipeline en maintenant tests.

**Démo (4-5 min):**
1. **[0:00-0:45]** Identifier code messy:
   - `backend/pipeline/stages/stage_3_market_analysis.py` (200 lignes)
   - Fonction monolithique
   - Variables mal nommées (`temp_var1`, `result2`)
   - Duplication de code
2. **[0:45-1:15]** Run tests actuels: ✅ 15 tests passent
3. **[1:15-2:00]** "Claude, analyse ce fichier et identifie problèmes"
   - Complexity: 45 (très élevé)
   - Code duplication: 35%
   - Poor naming: 12 variables
   - Missing docstrings
4. **[2:00-3:00]** "Refactorise en gardant tests verts"
   - Extrait 4 fonctions:
     - `extract_market_signals()`
     - `analyze_adoption_psychology()`
     - `generate_insights()`
     - `format_output()`
   - Renomme variables
   - Ajoute type hints
   - Docstrings
5. **[3:00-3:30]** Résultat:
   ```python
   # Avant: 200 lignes, complexity 45
   def run_stage_3(input_data):
       temp_var1 = ...
       result2 = ...
       # 180 lignes de logique imbriquée

   # Après: 80 lignes, complexity 12
   def run_stage_3(input_data: StageInput) -> StageOutput:
       """Analyze market adoption psychology."""
       signals = extract_market_signals(input_data)
       psychology = analyze_adoption_psychology(signals)
       insights = generate_insights(psychology)
       return format_output(insights)
   ```
6. **[3:30-4:00]** Re-run tests: ✅ 15 tests toujours passent
7. **[4:00-4:30]** Metrics:
   - Avant: 200 lignes, complexity 45
   - Après: 80 lignes, complexity 12
   - Tests: ✅ Identiques
8. **[4:30-4:45]** Commentaire: "Code propre sans casser fonctionnalité"

**Fichiers concernés:**
- `backend/pipeline/stages/stage_3_market_analysis.py`
- `backend/tests/test_stage_3.py`

---

#### **Sujet 19: Web Scraping Playwright - Sources de données**

**Statut:** ⚠️ **USE CASE À DÉFINIR**

**Ce qu'il y a:**
- Pipeline qui analyse documents
- Potentiel pour scraper trend reports

**Application:**
Scraper TrendHunter ou TrendWatching pour alimenter pipeline.

**Démo (5-6 min):**
1. **[0:00-0:30]** Besoin: "Alimenter pipeline avec dernières tendances TrendHunter"
2. **[0:30-1:00]** Vérifier robots.txt: "Claude, puis-je scraper trendhunter.com?"
3. **[1:00-2:00]** Claude + Playwright MCP:
   - Navigate vers trendhunter.com/trends
   - Identifie sélecteurs CSS
   - Extrait:
     - Trend title
     - Description
     - Category
     - Date published
4. **[2:00-3:00]** Structure données:
   ```json
   [
     {
       "title": "Sacred Sync - Digital Wellness",
       "description": "Consumers seeking...",
       "category": "Lifestyle",
       "date": "2024-01-15",
       "url": "https://trendhunter.com/trends/sacred-sync"
     }
   ]
   ```
5. **[3:00-4:00]** Sauvegarder dans DB:
   - Nouveau model Prisma: `TrendSource`
   - Import data via seed script
6. **[4:00-5:00]** Intégrer au pipeline:
   - Stage 1 utilise trend data comme input supplémentaire
   - Améliore pattern recognition
7. **[5:00-5:30]** Automatiser:
   - Cron job daily scrape
   - Claude crée GitHub Action
8. **[5:30-6:00]** Disclaimer éthique: respecte robots.txt, rate limiting

**Fichiers concernés:**
- `scripts/scrape-trends.ts` (nouveau)
- `innovation-web/prisma/schema.prisma` (add TrendSource model)
- `.github/workflows/scrape-trends.yml` (automation)

---

#### **Sujet 20: Multi-agent Swarms - Délégation complexe**

**Statut:** ✅ **AGENT PERSONAS DÉFINIS**

**Ce qu'il y a:**
- 6 agent personas documentés dans `agent-personas/`
- Pipeline 5 stages (peut être orchestré par swarm)

**Application:**
Orchestrer analyse innovation avec swarm de 6 agents spécialisés.

**Démo (6-7 min):**
1. **[0:00-0:45]** Tâche complexe: "Analyser innovation Savannah Bananas avec tous les angles"
2. **[0:45-1:30]** Initialiser swarm Claude-Flow:
   ```bash
   /claude-flow swarm init --topology hierarchical --max-agents 6
   ```
3. **[1:30-2:30]** Spawn 6 agents spécialisés:
   - **Pattern Hunter** (TRIZ/SIT analysis)
   - **Nature Translator** (Biomimicry)
   - **Market Psychologist** (Adoption psychology)
   - **Adversarial Analyst** (Red team validation)
   - **Strategic Oracle** (Foresight trends)
   - **Synthesis Orchestrator** (Integration)

4. **[2:30-4:30]** Délégation parallèle:
   - **Split screen montrant 6 agents**:
     - **Top-left**: Pattern Hunter analyse TRIZ contradictions
     - **Top-center**: Nature Translator cherche analogies nature
     - **Top-right**: Market Psychologist évalue adoption barriers
     - **Bottom-left**: Adversarial Analyst identifie risques
     - **Bottom-center**: Strategic Oracle projette 5-year trends
     - **Bottom-right**: Synthesis Orchestrator coordonne

5. **[4:30-5:30]** Chaque agent produit output:
   - Pattern Hunter: "5 TRIZ principles applicables"
   - Nature Translator: "3 biomimicry analogies (ant colonies, mycorrhizal networks)"
   - Market Psychologist: "User adoption score: 8.2/10"
   - Adversarial Analyst: "7 critical risks identified"
   - Strategic Oracle: "Trend alignment: 92%"

6. **[5:30-6:30]** Synthesis Orchestrator intègre:
   - Combine perspectives
   - Résout conflits (Pattern Hunter vs Adversarial)
   - Génère rapport unifié
   - Score final: 9.1/10 (vs 7.3/10 single agent)

7. **[6:30-6:50]** Metrics:
   - Temps: 8 min (vs 25 min sequential)
   - Qualité: 9.1/10 (vs 7.3/10)
   - Couverture: 6 perspectives (vs 1)

8. **[6:50-7:00]** Commentaire: "Swarms = équipe complète en minutes"

**Fichiers concernés:**
- `agent-personas/*.md` (6 agent definitions)
- `backend/pipeline/` (orchestré par swarm)

---

### ⚠️ **NÉCESSITE AJOUT** (2 sujets)

---

#### **Sujet 12: Stripe - Ajouter paiements**

**Statut:** ❌ **MANQUANT - Effort: 2-3h**

**Ce qui manque:**
- Stripe SDK
- Checkout flow
- Webhook handling
- Subscription management

**Effort pour ajouter:**
1. Install Stripe:
   ```bash
   npm install stripe @stripe/stripe-js @stripe/react-stripe-js
   ```
2. Créer routes API:
   - `innovation-web/app/api/stripe/checkout/route.ts`
   - `innovation-web/app/api/stripe/webhook/route.ts`
3. Ajouter Prisma model:
   ```prisma
   model Subscription {
     id String @id @default(uuid())
     userId String
     stripeCustomerId String
     stripePriceId String
     status String
     user User @relation(...)
   }
   ```
4. Frontend:
   - Pricing page
   - Checkout button
   - Success/cancel pages

**Démo après ajout (4-5 min):**
1. Pricing page: Free, Pro ($29/mo), Enterprise ($99/mo)
2. Click "Upgrade to Pro"
3. Stripe Checkout modal
4. Paiement test (4242 4242 4242 4242)
5. Webhook reçu → Update user subscription in DB
6. User accède features Pro (unlimited pipeline runs)

---

#### **Sujet 13: Hero Demo - Prototype complet en 1 jour**

**Statut:** ⚠️ **PRESQUE COMPLET - Manque Stripe**

**Ce qu'il y a:**
- ✅ Frontend Next.js
- ✅ Backend FastAPI
- ✅ Database Prisma
- ✅ Auth Clerk
- ✅ Storage Vercel Blob
- ✅ Deployment Vercel + Railway
- ❌ Stripe (nécessaire pour demo "SaaS payant")

**Après ajout Stripe, démo complète possible (15-20 min):**
- Phase 1: Spec (0-2min)
- Phase 2: Database (2-5min)
- Phase 3: Frontend + Auth (5-9min)
- Phase 4: Deployment (9-12min)
- Phase 5: Paiements (12-15min)
- Récap (15-16min)

---

## 🎯 Recommandations Finales

### **Tournage Immédiat (16 vidéos prêtes):**

**Quick Wins (3-4 min chacun):**
1. ✅ Sujet 2: Serena MCP
2. ✅ Sujet 9: Context7
3. ✅ Sujet 10: GitHub Review
4. ✅ Sujet 11: Clerk Auth
5. ✅ Sujet 14: Custom Instructions

**Stack & Méthodologie (4-6 min chacun):**
6. ✅ Sujet 1: FastAPI Debug
7. ✅ Sujet 3: Vercel/Railway Deploy
8. ✅ Sujet 6: Loop & Vérification
9. ✅ Sujet 7: Stack complète
10. ✅ Sujet 8: Prisma DB

**Avancé (5-7 min chacun):**
11. ✅ Sujet 4: Playwright Testing
12. ✅ Sujet 5: Sub-agents
13. ✅ Sujet 15: Memory Management
14. ✅ Sujet 16: Diagnostic Brownfield
15. ✅ Sujet 17: TDD
16. ✅ Sujet 18: Refactoring
17. ✅ Sujet 20: Swarms

**Use Case Spécifique (optionnel):**
18. ⚠️ Sujet 19: Web Scraping

---

### **Ajout Stripe (2-3h dev):**

Ensuite tourner:
19. ✅ Sujet 12: Stripe Payments
20. ✅ Sujet 13: Hero Demo

---

## 🚀 Plan de Production Recommandé

### **Semaine 1-2: Quick Wins (5 vidéos)**
Tournez les sujets faciles pour valider workflow et qualité.

### **Semaine 3-4: Stack & Deploy (5 vidéos)**
Démontrez la stack complète et deployment.

### **Semaine 5-6: Méthodologie Avancée (6 vidéos)**
Différenciez-vous avec sub-agents, swarms, TDD.

### **Semaine 7: Ajout Stripe + Hero Demo (2 vidéos)**
Complétez avec paiements et demo end-to-end.

### **Optionnel: Web Scraping (1 vidéo)**
Si use case pertinent identifié.

---

**TOTAL: 18 vidéos immédiatement + 2 après Stripe = 20 vidéos complètes**

🎉 **Repo parfait pour série vidéo Newcode!**
