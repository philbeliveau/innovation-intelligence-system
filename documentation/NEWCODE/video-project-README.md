# Projet Vidéos Newcode - Documentation de Travail

## 🎯 Objectif du Projet

Créer une série de **20 vidéos courtes** (2-7 min) pour démontrer les méthodologies et techniques Newcode en programmation agentique. Ces vidéos seront des enregistrements d'écran avec commentaire, montrant des manipulations concrètes et convaincantes.

## 📋 Contexte

Ce projet fait partie de la stratégie de contenu Newcode pour:
- Démontrer la valeur de la programmation agentique
- Montrer des techniques avancées (MCP, sub-agents, swarms, TDD)
- Attirer des clients potentiels pour formations
- Créer du contenu viral sur LinkedIn/YouTube

**Repo de démonstration**: [`innovation-intelligence-system`](https://github.com/philbeliveau/innovation-intelligence-system)
**Branche**: `architecture-cleanup-prisma`

## 📹 Les 20 Sujets Vidéo (Propositions Initiales)

### Méthodologie MCP (Model Context Protocol)
1. **FastAPI MCP** - Debugger une application FastAPI
2. **Serena MCP** - Économiser des tokens LLM intelligemment
3. **Vercel & Railway MCP** - Déployer sans être DevOps
4. **Playwright MCP** - Tester automatiquement
9. **Context7 MCP** - Documentation toujours à jour
10. **GitHub MCP** - Code review automatisé
11. **Clerk MCP** - Authentication en 10 minutes
8. **Prisma MCP** - Créer et migrer des bases de données

### Techniques Avancées
5. **Sub-agents** - Déléguer la lecture, garder le contrôle
6. **Loop & Vérification** - Développer des systèmes robustes
14. **Custom Instructions (CLAUDE.md)** - Agent personnalisé
15. **Memory & Context Management** - Projets complexes
16. **Diagnostic Brownfield** - Documenter projet existant
17. **TDD** - Tests avant code
18. **Refactoring automatisé** - Dette technique
19. **Web Scraping Playwright** - Sources de données
20. **Multi-agent Swarms** - Délégation complexe

### Stack Moderne
7. **La Stack Moderne** - Vue d'ensemble (Railway, Vercel, Prisma, Clerk, Stripe)
12. **Stripe** - Ajouter paiements (nécessite ajout au repo)
13. **Hero Demo** - Prototype complet en 1 jour (nécessite Stripe)

## 📄 Documents de Travail

### Document Principal (CE FICHIER)
**`video-subjects-innovation-repo-mapping-UPDATED.md`**

Ce document contient l'analyse complète de tous les 20 sujets vidéo avec:
- ✅ **Statut** de chaque sujet (prêt / nécessite ajout / à définir)
- **Ce qu'il y a** dans le repo actuel
- **Scénario de démo détaillé** (timestampé)
- **Fichiers concernés** (chemins exacts)
- **Effort requis** si features manquantes

### ⚠️ IMPORTANT: Ce sont des PROPOSITIONS

Les scénarios détaillés dans le document principal sont des **propositions initiales** qui seront **adaptées et modifiées** selon:
- Les besoins réels identifiés lors de la préparation
- Les découvertes faites en explorant le repo innovation
- Les choix pédagogiques lors du tournage
- Les contraintes techniques rencontrées

**Ce document sert de BASE DE TRAVAIL**, pas de script final.

## 🔄 Workflow de Production

### Phase 1: Préparation (EN COURS)
- [x] Analyse du repo innovation-intelligence-system
- [x] Mapping des 20 sujets → repo capabilities
- [ ] Révision et adaptation des scénarios avec équipe
- [ ] Priorisation des sujets (ordre de tournage)

### Phase 2: Ajustements Techniques (SI NÉCESSAIRE)
- [ ] Ajouter Stripe (2-3h) pour Sujets 12 & 13
- [ ] Définir use case pour Sujet 19 (Web Scraping)
- [ ] Créer structure `.context/` pour Sujet 15

### Phase 3: Tournage
- [ ] Semaine 1-2: Quick Wins (5 vidéos)
- [ ] Semaine 3-4: Stack & Deploy (5 vidéos)
- [ ] Semaine 5-6: Méthodologie Avancée (6 vidéos)
- [ ] Semaine 7: Stripe + Hero Demo (2 vidéos)

### Phase 4: Post-Production
- [ ] Montage
- [ ] Ajout de titres/annotations
- [ ] Publication sur LinkedIn/YouTube
- [ ] Intégration dans formations Newcode

## 🎬 Statut Actuel

### Vidéos Prêtes à Tourner Immédiatement (18/20)
Le repo `innovation-intelligence-system` (branche `architecture-cleanup-prisma`) contient TOUS les composants nécessaires pour 18 vidéos:

**Stack Technique Confirmée:**
- ✅ Next.js 15 + React 19 + TypeScript
- ✅ FastAPI + LangChain pipeline
- ✅ Prisma + PostgreSQL (6 models)
- ✅ Clerk Auth
- ✅ Vercel Blob storage
- ✅ Tests: Jest + pytest
- ✅ Deployment docs: Vercel + Railway

### Vidéos Nécessitant Ajouts (2/20)
- **Sujet 12 (Stripe)**: Nécessite intégration Stripe (~2-3h dev)
- **Sujet 13 (Hero Demo)**: Nécessite Stripe pour démo SaaS complète

## 📊 Plan de Production Recommandé

### Approche Recommandée: Itérative

1. **Tourner 5 vidéos "Quick Wins"** d'abord (Sujets 2, 9, 10, 11, 14)
   - Valider workflow de tournage
   - Obtenir feedback
   - Ajuster scénarios si nécessaire

2. **Tourner 5 vidéos "Stack & Deploy"** (Sujets 1, 3, 6, 7, 8)
   - Montrer valeur de la stack moderne
   - Démontrer expertise technique

3. **Tourner 6 vidéos "Méthodologie Avancée"** (Sujets 4, 5, 15, 16, 17, 18, 20)
   - Différenciation Newcode
   - Techniques propriétaires

4. **Ajouter Stripe + Tourner dernières vidéos** (Sujets 12, 13)
   - Compléter la série

## 🤝 Collaboration avec Autres Agents

Ce projet nécessite collaboration avec:
- **Agent Analyst** - Pour diagnostic approfondi du repo innovation
- **Agent Coder** - Pour ajout features manquantes (Stripe, etc.)
- **Agent Tester** - Pour validation des démos
- **Agent Documenter** - Pour scripts finaux

## 📝 Notes de Travail

### Décisions à Prendre
- [ ] Ordre exact de tournage des 20 vidéos
- [ ] Durée cible par vidéo (actuellement 2-7 min selon complexité)
- [ ] Faut-il ajouter Stripe AVANT de tourner, ou tourner 18 vidéos d'abord?
- [ ] Use case précis pour Web Scraping (Sujet 19)

### Contraintes Identifiées
- Repo est public (bon pour démo)
- Branche `architecture-cleanup-prisma` est stable
- Pas de Stripe actuellement (2-3h pour ajouter)
- Railway database doit être provisionné (nécessite compte)

### Opportunités
- Repo est **parfait** pour démontrer méthodologie avancée
- 24 research docs fournissent contexte riche
- 6 agent personas permettent démo swarms
- Stack moderne complète (sauf Stripe)

## 🔗 Ressources

- **Repo Innovation**: https://github.com/philbeliveau/innovation-intelligence-system
- **Branche Active**: `architecture-cleanup-prisma`
- **Document Mapping Détaillé**: `video-subjects-innovation-repo-mapping-UPDATED.md`
- **Circle Community**: ID 380548 (pour publication futures des vidéos en lessons)

---

**Dernière mise à jour**: 2025-01-25
**Statut**: 📋 Préparation - Mapping complet, prêt pour révision d'équipe
