import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import yaml from 'js-yaml'

export async function GET() {
  try {
    const cookieStore = await cookies()
    const companyId = cookieStore.get('company_id')?.value

    if (!companyId) {
      return NextResponse.json(
        { error: 'No company selected' },
        { status: 401 }
      )
    }

    // Sanitize company_id to prevent path traversal attacks
    const sanitizedId = companyId.replace(/[^a-z0-9-]/gi, '')

    if (sanitizedId !== companyId) {
      return NextResponse.json(
        { error: 'Invalid company identifier' },
        { status: 400 }
      )
    }

    // Load YAML file from data/brand-profiles/ (within innovation-web directory for Vercel deployment)
    const yamlPath = path.join(process.cwd(), 'data', 'brand-profiles', `${sanitizedId}.yaml`)

    if (!fs.existsSync(yamlPath)) {
      return NextResponse.json(
        { error: 'Company profile not found' },
        { status: 404 }
      )
    }

    const fileContents = fs.readFileSync(yamlPath, 'utf8')
    const profile = yaml.load(fileContents) as { brand_name: string }

    return NextResponse.json({
      company_id: companyId,
      company_name: profile.brand_name
    })
  } catch (error) {
    console.error('Error loading company profile:', error)
    return NextResponse.json(
      { error: 'Failed to load company profile' },
      { status: 500 }
    )
  }
}
