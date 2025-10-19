import { exec } from 'child_process'
import { promisify } from 'util'
import { NextResponse } from 'next/server'

const execAsync = promisify(exec)

export async function GET() {
  try {
    // Test Python version
    const { stdout: pythonVersion, stderr: pythonError } = await execAsync('python3 --version')

    // Test if pipeline directory exists
    const { stdout: lsOutput } = await execAsync('ls -la ../../pipeline 2>&1 || echo "Pipeline directory not found"')

    // Test Python package availability
    let pipList = 'Not available'
    try {
      const { stdout: pipOutput } = await execAsync('python3 -m pip list')
      pipList = pipOutput
    } catch (error) {
      pipList = 'pip command failed'
    }

    return NextResponse.json({
      success: !pythonError,
      pythonVersion: pythonVersion.trim(),
      pythonError: pythonError || null,
      pipelineDirectory: lsOutput,
      pipPackages: pipList,
      workingDirectory: process.cwd(),
      environment: process.env.NODE_ENV,
    })
  } catch (err) {
    return NextResponse.json({
      success: false,
      error: err instanceof Error ? err.message : 'Unknown error',
      workingDirectory: process.cwd(),
    }, { status: 500 })
  }
}
