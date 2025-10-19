import { NextRequest, NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import { load } from 'js-yaml'
import { join } from 'path'
import { cookies } from 'next/headers'

const ALLOWED_COMPANIES = ['lactalis-canada', 'mccormick-usa', 'columbia-sportswear', 'decathlon']

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { company_id } = body

    // Validate company_id
    if (!company_id || !ALLOWED_COMPANIES.includes(company_id)) {
      return NextResponse.json(
        { error: 'Invalid company ID. Must be one of: ' + ALLOWED_COMPANIES.join(', ') },
        { status: 400 }
      )
    }

    // Construct path to YAML file (within innovation-web directory)
    const yamlPath = join(process.cwd(), 'data', 'brand-profiles', `${company_id}.yaml`)

    // Read YAML file
    let yamlContent: string
    try {
      yamlContent = await readFile(yamlPath, 'utf-8')
    } catch (error) {
      console.error(`Failed to read YAML file at ${yamlPath}:`, error)
      return NextResponse.json(
        { error: 'Company profile not found' },
        { status: 500 }
      )
    }

    // Parse YAML
    let profile: { brand_name?: string }
    try {
      profile = load(yamlContent) as { brand_name?: string }
    } catch (error) {
      console.error(`Failed to parse YAML for ${company_id}:`, error)
      return NextResponse.json(
        { error: 'Invalid company profile format' },
        { status: 500 }
      )
    }

    // Set HTTP-only cookie
    const cookieStore = await cookies()
    cookieStore.set('company_id', company_id, {
      httpOnly: true,
      maxAge: 604800, // 7 days in seconds
      sameSite: 'lax',
      path: '/',
    })

    // Return success response
    return NextResponse.json({
      company_name: profile.brand_name || company_id,
      company_id,
    })
  } catch (error) {
    console.error('Unexpected error in set-company route:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
