-- CreateEnum
CREATE TYPE "RunStatus" AS ENUM ('PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED');

-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "clerkId" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "name" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PipelineRun" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "documentName" TEXT NOT NULL,
    "documentUrl" TEXT,
    "companyName" TEXT NOT NULL,
    "status" "RunStatus" NOT NULL DEFAULT 'PROCESSING',
    "pipelineVersion" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "completedAt" TIMESTAMP(3),
    "duration" INTEGER,

    CONSTRAINT "PipelineRun_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "OpportunityCard" (
    "id" TEXT NOT NULL,
    "runId" TEXT NOT NULL,
    "number" INTEGER NOT NULL,
    "title" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "isStarred" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "OpportunityCard_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "InspirationReport" (
    "id" TEXT NOT NULL,
    "runId" TEXT NOT NULL,
    "selectedTrack" TEXT NOT NULL,
    "nonSelectedTrack" TEXT NOT NULL,
    "stage1Output" TEXT NOT NULL,
    "stage2Output" TEXT NOT NULL,
    "stage3Output" TEXT NOT NULL,
    "stage4Output" TEXT NOT NULL,
    "stage5Output" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "InspirationReport_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "StageOutput" (
    "id" TEXT NOT NULL,
    "runId" TEXT NOT NULL,
    "stageNumber" INTEGER NOT NULL,
    "stageName" TEXT NOT NULL,
    "status" "RunStatus" NOT NULL,
    "output" TEXT NOT NULL,
    "completedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "StageOutput_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_clerkId_key" ON "User"("clerkId");

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- CreateIndex
CREATE INDEX "User_clerkId_idx" ON "User"("clerkId");

-- CreateIndex
CREATE INDEX "PipelineRun_userId_createdAt_idx" ON "PipelineRun"("userId", "createdAt");

-- CreateIndex
CREATE INDEX "PipelineRun_status_idx" ON "PipelineRun"("status");

-- CreateIndex
CREATE INDEX "OpportunityCard_runId_number_idx" ON "OpportunityCard"("runId", "number");

-- CreateIndex
CREATE INDEX "OpportunityCard_isStarred_idx" ON "OpportunityCard"("isStarred");

-- CreateIndex
CREATE UNIQUE INDEX "OpportunityCard_runId_number_key" ON "OpportunityCard"("runId", "number");

-- CreateIndex
CREATE UNIQUE INDEX "InspirationReport_runId_key" ON "InspirationReport"("runId");

-- CreateIndex
CREATE INDEX "StageOutput_runId_stageNumber_idx" ON "StageOutput"("runId", "stageNumber");

-- CreateIndex
CREATE UNIQUE INDEX "StageOutput_runId_stageNumber_key" ON "StageOutput"("runId", "stageNumber");

-- AddForeignKey
ALTER TABLE "PipelineRun" ADD CONSTRAINT "PipelineRun_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "OpportunityCard" ADD CONSTRAINT "OpportunityCard_runId_fkey" FOREIGN KEY ("runId") REFERENCES "PipelineRun"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "InspirationReport" ADD CONSTRAINT "InspirationReport_runId_fkey" FOREIGN KEY ("runId") REFERENCES "PipelineRun"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "StageOutput" ADD CONSTRAINT "StageOutput_runId_fkey" FOREIGN KEY ("runId") REFERENCES "PipelineRun"("id") ON DELETE CASCADE ON UPDATE CASCADE;
