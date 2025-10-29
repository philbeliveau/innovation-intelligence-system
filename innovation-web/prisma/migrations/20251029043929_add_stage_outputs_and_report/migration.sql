-- AlterTable
ALTER TABLE "PipelineRun" ADD COLUMN     "fullReportMarkdown" TEXT,
ADD COLUMN     "stage1Output" JSONB,
ADD COLUMN     "stage2Output" JSONB,
ADD COLUMN     "stage3Output" JSONB,
ADD COLUMN     "stage4Output" JSONB;
