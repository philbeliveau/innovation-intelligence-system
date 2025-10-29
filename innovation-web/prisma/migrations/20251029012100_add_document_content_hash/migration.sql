-- AlterTable (add column if it doesn't exist)
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'Document' AND column_name = 'contentHash'
    ) THEN
        ALTER TABLE "Document" ADD COLUMN "contentHash" TEXT;
    END IF;
END $$;

-- CreateIndex (only if doesn't exist)
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'Document_contentHash_idx'
    ) THEN
        CREATE INDEX "Document_contentHash_idx" ON "Document"("contentHash");
    END IF;
END $$;

-- CreateIndex (only if doesn't exist)
DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes WHERE indexname = 'Document_userId_contentHash_key'
    ) THEN
        CREATE UNIQUE INDEX "Document_userId_contentHash_key" ON "Document"("userId", "contentHash");
    END IF;
END $$;
