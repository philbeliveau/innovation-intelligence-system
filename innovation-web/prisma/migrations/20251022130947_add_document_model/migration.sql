/*
  Warnings:

  - You are about to drop the column `companyId` on the `Document` table. All the data in the column will be lost.
  - You are about to drop the column `fileType` on the `Document` table. All the data in the column will be lost.
  - You are about to drop the column `updatedAt` on the `Document` table. All the data in the column will be lost.

*/
-- DropIndex
DROP INDEX "public"."Document_companyId_idx";

-- DropIndex
DROP INDEX "public"."Document_userId_uploadedAt_idx";

-- AlterTable
ALTER TABLE "Document" DROP COLUMN "companyId",
DROP COLUMN "fileType",
DROP COLUMN "updatedAt",
ADD COLUMN     "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ALTER COLUMN "uploadedAt" DROP DEFAULT;

-- CreateIndex
CREATE INDEX "Document_userId_createdAt_idx" ON "Document"("userId", "createdAt");
