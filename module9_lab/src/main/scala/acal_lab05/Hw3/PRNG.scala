package acal_lab05.Hw3

import chisel3._
import chisel3.util._

class PRNG(seed: Int) extends Module {
  val io = IO(new Bundle {
    val gen    = Input(Bool())
    val puzzle = Output(Vec(4, UInt(4.W)))
    val ready  = Output(Bool())
  })

  // 1. 核心暫存器：LFSR 與一個額外的擾動計數器
  val lfsr = RegInit((seed ^ 0xACE1).U(16.W))
  val roundCount = RegInit(0.U(8.W)) 
  val state = RegInit(0.U(2.W))
  val sIdle = 0.U; val sRun = 1.U; val sDone = 2.U

  // 2. LFSR 標準位移 (16-bit)
  def shift(c: UInt): UInt = {
    val feedback = c(15) ^ c(13) ^ c(12) ^ c(10)
    Cat(c(14, 0), feedback)
  }

  // 3. 初始對映：使用不同的 bit 段並加上 roundCount 確保每輪基底不同
  val d0 = Wire(UInt(4.W)); d0 := (lfsr(3, 0)   + roundCount) % 10.U
  val d1 = Wire(UInt(4.W)); d1 := (lfsr(7, 4)   + roundCount + 1.U) % 10.U
  val d2 = Wire(UInt(4.W)); d2 := (lfsr(11, 8)  + roundCount + 2.U) % 10.U
  val d3 = Wire(UInt(4.W)); d3 := (lfsr(15, 12) + roundCount + 3.U) % 10.U

  // 4. 解決重複問題：遞增法 (Incremental Fix)
  // 如果 d1 重複了 d0，就讓 d1 加 1；以此類推。
  val fix1 = Mux(d1 === d0, (d1 + 1.U) % 10.U, d1)
  
  val fix2_tmp = Mux(d2 === d0 || d2 === fix1, (d2 + 1.U) % 10.U, d2)
  val fix2 = Mux(fix2_tmp === d0 || fix2_tmp === fix1, (fix2_tmp + 1.U) % 10.U, fix2_tmp)
  
  val fix3_tmp1 = Mux(d3 === d0 || d3 === fix1 || d3 === fix2, (d3 + 1.U) % 10.U, d3)
  val fix3_tmp2 = Mux(fix3_tmp1 === d0 || fix3_tmp1 === fix1 || fix3_tmp1 === fix2, (fix3_tmp1 + 1.U) % 10.U, fix3_tmp1)
  val fix3 = Mux(fix3_tmp2 === d0 || fix3_tmp2 === fix1 || fix3_tmp2 === fix2, (fix3_tmp2 + 1.U) % 10.U, fix3_tmp2)

  // 5. 狀態機邏輯
  switch(state) {
    is(sIdle) {
      when(io.gen) { 
        state := sRun 
        lfsr := shift(shift(shift(lfsr))) // 跳三步增加隨機性
      }
    }
    is(sRun) {
      // 在這個架構下，fix0-3 已經保證不重複且在 0-9 範圍內
      state := sDone
      roundCount := roundCount + 1.U // 每完成一組謎題，擾動計數器就加 1
    }
    is(sDone) {
      when(io.gen) { 
        state := sRun
        lfsr := shift(shift(shift(lfsr)))
      }
    }
  }

  io.ready := (state === sDone)
  io.puzzle(0) := d0
  io.puzzle(1) := fix1
  io.puzzle(2) := fix2
  io.puzzle(3) := fix3
}