/**
 * GET /api/pipeline/[runId]/download/stage1
 *
 * Download Stage 1 mechanism extraction report as PDF
 */

import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { jsPDF } from 'jspdf';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  try {
    const { runId } = await params;

    // Fetch Stage 1 data from database
    const stageOutput = await prisma.stageOutput.findUnique({
      where: {
        runId_stageNumber: {
          runId,
          stageNumber: 1,
        },
      },
      include: {
        run: {
          select: {
            documentName: true,
            companyName: true,
            createdAt: true,
          },
        },
      },
    });

    if (!stageOutput) {
      return NextResponse.json(
        { error: 'Pipeline run not found or Stage 1 not completed' },
        { status: 404 }
      );
    }

    // Parse Stage 1 output JSON
    let stage1Data;
    try {
      stage1Data = JSON.parse(stageOutput.output);
    } catch (e) {
      return NextResponse.json(
        { error: 'Failed to parse Stage 1 output data' },
        { status: 500 }
      );
    }

    // Generate PDF
    const pdf = new jsPDF();
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 20;
    const maxWidth = pageWidth - (margin * 2);
    let yPosition = margin;

    // Helper to add text with automatic page breaks
    const addText = (text: string, fontSize: number, isBold: boolean = false) => {
      pdf.setFontSize(fontSize);
      pdf.setFont('helvetica', isBold ? 'bold' : 'normal');

      const lines = pdf.splitTextToSize(text, maxWidth);

      lines.forEach((line: string) => {
        if (yPosition + 10 > pageHeight - margin) {
          pdf.addPage();
          yPosition = margin;
        }
        pdf.text(line, margin, yPosition);
        yPosition += fontSize * 0.5;
      });

      yPosition += 5; // Add spacing after paragraph
    };

    // Header
    pdf.setFillColor(91, 154, 153); // Teal color #5B9A99
    pdf.rect(0, 0, pageWidth, 30, 'F');
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(20);
    pdf.setFont('helvetica', 'bold');
    pdf.text('Stage 1: Mechanism Extraction Report', margin, 20);

    yPosition = 45;
    pdf.setTextColor(0, 0, 0);

    // Document Info
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`Document: ${stageOutput.run.documentName}`, margin, yPosition);
    yPosition += 7;
    pdf.text(`Company: ${stageOutput.run.companyName}`, margin, yPosition);
    yPosition += 7;
    pdf.text(
      `Generated: ${new Date(stageOutput.run.createdAt).toLocaleString()}`,
      margin,
      yPosition
    );
    yPosition += 15;

    // Trend Title
    if (stage1Data.trendTitle) {
      addText(`Trend: ${stage1Data.trendTitle}`, 14, true);
    }

    // Core Mechanism
    if (stage1Data.coreMechanism) {
      addText('Core Mechanism:', 12, true);
      addText(stage1Data.coreMechanism, 11, false);
    }

    // Business Impact
    if (stage1Data.businessImpact) {
      addText('Business Impact:', 12, true);
      addText(stage1Data.businessImpact, 11, false);
    }

    // Pattern Transfers To
    if (stage1Data.patternTransfersTo && stage1Data.patternTransfersTo.length > 0) {
      addText('Applicable Industries:', 12, true);
      stage1Data.patternTransfersTo.forEach((industry: string) => {
        addText(`• ${industry}`, 11, false);
      });
    }

    // Mechanisms Detail
    if (stage1Data.mechanisms && stage1Data.mechanisms.length > 0) {
      yPosition += 5;
      addText('Detailed Mechanisms:', 14, true);

      stage1Data.mechanisms.forEach(
        (
          mechanism: {
            title?: string
            concreteExample?: string
            underlyingMechanism?: string
            mechanismType?: string
            constraintEliminated?: string
            whyItWorks?: string
          },
          index: number
        ) => {
          addText(`Mechanism ${index + 1}: ${mechanism.title || 'Untitled'}`, 12, true)

          if (mechanism.concreteExample) {
            addText(`Example: ${mechanism.concreteExample}`, 10, false)
          }

          if (mechanism.underlyingMechanism) {
            addText(`Pattern: ${mechanism.underlyingMechanism}`, 10, false)
          }

          if (mechanism.mechanismType) {
            addText(`Type: ${mechanism.mechanismType}`, 10, false)
          }

          if (mechanism.constraintEliminated) {
            addText(`Constraint Eliminated: ${mechanism.constraintEliminated}`, 10, false)
          }

          if (mechanism.whyItWorks) {
            addText(`Why It Works: ${mechanism.whyItWorks}`, 10, false)
          }

          yPosition += 5
        }
      )
    }

    // Extracted Text Summary
    if (stage1Data.extractedText) {
      yPosition += 5;
      addText('Document Summary:', 12, true);
      addText(stage1Data.extractedText, 10, false);
    }

    // Quality Metrics
    yPosition += 5;
    addText('Analysis Quality:', 12, true);

    if (stage1Data.evidenceStrength) {
      addText(`Evidence Strength: ${stage1Data.evidenceStrength}`, 10, false);
    }

    if (stage1Data.abstractionTest) {
      addText(`Abstraction Test: ${stage1Data.abstractionTest}`, 10, false);
    }

    if (stage1Data.cpgRelevance) {
      addText(`CPG Relevance: ${stage1Data.cpgRelevance}`, 10, false);
    }

    // Footer
    const totalPages = pdf.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
      pdf.setPage(i);
      pdf.setFontSize(8);
      pdf.setTextColor(128, 128, 128);
      pdf.text(
        `Page ${i} of ${totalPages} | Run ID: ${runId}`,
        margin,
        pageHeight - 10
      );
    }

    // Generate PDF buffer
    const pdfBuffer = pdf.output('arraybuffer');

    // Return PDF with proper headers
    return new NextResponse(pdfBuffer, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="stage1-report-${runId}.pdf"`,
      },
    });
  } catch (error) {
    console.error('Stage 1 PDF generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate PDF' },
      { status: 500 }
    );
  }
}
