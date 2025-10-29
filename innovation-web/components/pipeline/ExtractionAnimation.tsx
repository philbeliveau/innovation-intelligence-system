/**
 * ExtractionAnimation Component
 * Animated coffee machine visualization for Stage 1 extraction process
 * Displays brewing animation while processing, error state if failed
 */

'use client'

import React from 'react'
import BOIBadge from './BOIBadge'

export interface ExtractionAnimationProps {
  status: 'running' | 'error'
  elapsedTime?: number
}

const CoffeeMachineAnimation = ({ isAnimating }: { isAnimating: boolean }) => (
  <div className="relative w-[300px] h-[280px] mx-auto">
    <style jsx>{`
      @keyframes liquid {
        0% { height: 0px; opacity: 1; }
        5% { height: 0px; opacity: 1; }
        20% { height: 62px; opacity: 1; }
        95% { height: 62px; opacity: 1; }
        100% { height: 62px; opacity: 0; }
      }
      @keyframes smokeOne {
        0% { bottom: 20px; opacity: 0; }
        40% { bottom: 50px; opacity: 0.5; }
        80% { bottom: 80px; opacity: 0.3; }
        100% { bottom: 80px; opacity: 0; }
      }
      @keyframes smokeTwo {
        0% { bottom: 40px; opacity: 0; }
        40% { bottom: 70px; opacity: 0.5; }
        80% { bottom: 80px; opacity: 0.3; }
        100% { bottom: 80px; opacity: 0; }
      }
      .liquid-animate {
        animation: liquid 4s 4s linear infinite;
      }
      .smoke-one {
        animation: smokeOne 3s 4s linear infinite;
      }
      .smoke-two {
        animation: smokeTwo 3s 5s linear infinite;
      }
      .smoke-three {
        animation: smokeTwo 3s 6s linear infinite;
      }
      .smoke-four {
        animation: smokeOne 3s 5s linear infinite;
      }
    `}</style>

    {/* Coffee Header */}
    <div
      className="absolute top-0 left-0 w-full h-[80px] rounded-[10px]"
      style={{ backgroundColor: '#ddcfcc' }}
    >
      {/* Button One */}
      <div
        className="absolute top-[25px] left-[15px] w-[25px] h-[25px] rounded-full"
        style={{ backgroundColor: '#282323' }}
      >
        <div
          className="absolute bottom-[-8px] left-[calc(50%-4px)] w-[8px] h-[8px]"
          style={{ backgroundColor: '#615e5e' }}
        />
      </div>

      {/* Button Two */}
      <div
        className="absolute top-[25px] left-[50px] w-[25px] h-[25px] rounded-full"
        style={{ backgroundColor: '#282323' }}
      >
        <div
          className="absolute bottom-[-8px] left-[calc(50%-4px)] w-[8px] h-[8px]"
          style={{ backgroundColor: '#615e5e' }}
        />
      </div>

      {/* Display - Teal accent */}
      <div
        className="absolute top-[calc(50%-25px)] left-[calc(50%-25px)] w-[50px] h-[50px] rounded-full border-[5px] box-border"
        style={{
          backgroundColor: '#9acfc5',
          borderColor: '#43beae'
        }}
      />

      {/* Details */}
      <div
        className="absolute top-[10px] right-[10px] w-[8px] h-[20px]"
        style={{
          backgroundColor: '#9b9091',
          boxShadow: '-12px 0 0 #9b9091, -24px 0 0 #9b9091'
        }}
      />
    </div>

    {/* Coffee Medium */}
    <div
      className="absolute top-[80px] left-[calc(50%-45%)] w-[90%] h-[160px]"
      style={{ backgroundColor: '#bcb0af' }}
    >
      {/* Base */}
      <div
        className="absolute bottom-0 left-[calc(50%-45%)] w-[90%] h-[100px] rounded-t-[20px]"
        style={{ backgroundColor: '#776f6e' }}
      />

      {/* Exit Spout */}
      <div
        className="absolute top-0 left-[calc(50%-30px)] w-[60px] h-[20px]"
        style={{ backgroundColor: '#231f20' }}
      >
        <div
          className="absolute bottom-[-20px] left-[calc(50%-25px)] w-[50px] h-[20px]"
          style={{
            backgroundColor: '#231f20',
            borderRadius: '0 0 50% 50%'
          }}
        />
        <div
          className="absolute bottom-[-30px] left-[calc(50%-5px)] w-[10px] h-[10px]"
          style={{ backgroundColor: '#231f20' }}
        />
      </div>

      {/* Arm */}
      <div
        className="absolute top-[15px] right-[25px] w-[70px] h-[20px]"
        style={{ backgroundColor: '#231f20' }}
      >
        <div
          className="absolute top-[7px] left-[-15px] w-[15px] h-[5px]"
          style={{ backgroundColor: '#9e9495' }}
        />
      </div>

      {/* Cup */}
      <div
        className="absolute bottom-0 left-[calc(50%-40px)] w-[80px] h-[47px] bg-white"
        style={{
          borderRadius: '0 0 70px 70px / 0 0 110px 110px'
        }}
      >
        {/* Cup Handle */}
        <div
          className="absolute top-[6px] right-[-13px] w-[20px] h-[20px] rounded-full border-[5px] border-white"
        />
      </div>

      {/* Liquid Animation - Teal colored */}
      {isAnimating && (
        <div
          className="absolute top-[50px] left-[calc(50%-3px)] w-[6px] opacity-0 liquid-animate"
          style={{
            height: '63px',
            backgroundColor: '#5B9A99'
          }}
        />
      )}

      {/* Steam/Smoke */}
      {isAnimating && (
        <>
          <div
            className="absolute left-[102px] w-[8px] h-[20px] rounded-[5px] opacity-0 smoke-one"
            style={{
              bottom: '50px',
              backgroundColor: '#b3aeae'
            }}
          />
          <div
            className="absolute left-[118px] w-[8px] h-[20px] rounded-[5px] opacity-0 smoke-two"
            style={{
              bottom: '70px',
              backgroundColor: '#b3aeae'
            }}
          />
          <div
            className="absolute right-[118px] w-[8px] h-[20px] rounded-[5px] opacity-0 smoke-three"
            style={{
              bottom: '65px',
              backgroundColor: '#b3aeae'
            }}
          />
          <div
            className="absolute right-[102px] w-[8px] h-[20px] rounded-[5px] opacity-0 smoke-four"
            style={{
              bottom: '50px',
              backgroundColor: '#b3aeae'
            }}
          />
        </>
      )}
    </div>

    {/* Coffee Footer - Teal accent */}
    <div
      className="absolute bottom-[25px] left-[calc(50%-47.5%)] w-[95%] h-[15px] rounded-[10px]"
      style={{ backgroundColor: '#41bdad' }}
    >
      <div
        className="absolute bottom-[-25px] left-[-8px] w-[106%] h-[26px]"
        style={{ backgroundColor: '#000' }}
      />
    </div>
  </div>
)

export default function ExtractionAnimation({ status, elapsedTime }: ExtractionAnimationProps) {
  const isRunning = status === 'running'
  const isError = status === 'error'

  return (
    <div className="relative h-full flex flex-col items-center justify-center p-4 md:p-6">
      {/* BOI Badge - scales down on mobile */}
      <div className="scale-80 md:scale-100">
        <BOIBadge size="medium" />
      </div>

      {/* Error overlay */}
      {isError && (
        <div className="absolute inset-0 bg-red-500 opacity-20 rounded-lg pointer-events-none" />
      )}

      {/* Main content */}
      <div className="text-center space-y-4 md:space-y-6 w-full">
        {/* Coffee Machine illustration or error icon */}
        {isError ? (
          <div className="text-5xl md:text-6xl mb-4" aria-label="Error">
            ⚠️
          </div>
        ) : (
          <div className="scale-90 md:scale-100">
            <CoffeeMachineAnimation isAnimating={isRunning} />
          </div>
        )}

        {/* Status text */}
        <div className="space-y-2 px-4 md:px-0">
          <h3 className="text-lg md:text-xl font-semibold text-gray-900">
            {isError ? 'Extraction encountered an error' : 'Extracting transferable insights from your document'}
          </h3>

          {isRunning && elapsedTime && (
            <p className="text-sm text-gray-500">
              Elapsed time: {Math.floor(elapsedTime / 1000)}s
            </p>
          )}
        </div>

        {/* Processing indicator for running state */}
        {isRunning && (
          <div className="flex items-center justify-center gap-2 mt-4">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-teal-100 border-t-[#5B9A99]" />
            <span className="text-sm text-gray-500">Processing...</span>
          </div>
        )}
      </div>
    </div>
  )
}
