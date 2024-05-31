import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

MASTER_CLOCK = 2_000_000 # 2MHZ

async def reset(dut):
    master_clock = MASTER_CLOCK # // 8
    cycle_in_nanoseconds = 1e9 / master_clock # 1 / 2Mhz / nanosecond
    dut._log.info("start")
    clock = Clock(dut.clk, cycle_in_nanoseconds, units="ns")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.clock_select.value = 0
    dut.bc1.value = 1
    dut.bdir.value = 1

    dut._log.info("reset")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

async def done(dut):
    # await ClockCycles(dut.clk, 1)
    dut._log.info("DONE!")

async def set_register(dut, reg, val):
    # dut.uio_in.value =       0b000000_11 # Latch register index
    # Latch register index
    dut.bc1.value = 1
    dut.bdir.value = 1
    dut.data.value  = reg & 15
    await ClockCycles(dut.clk, 2)
    # print_chip_state(dut)
    # dut.uio_in.value =       0b000000_10 # Write value to register
    dut.bc1.value = 0
    dut.bdir.value = 1
    dut.data.value  = val
    await ClockCycles(dut.clk, 1)
    # print_chip_state(dut)
    # dut.uio_in.value =       0b000000_00 # Inactivate: disable writes and trigger envelope restart, if last write was to Envelope register
    dut.bc1.value = 0
    dut.bdir.value = 0
    dut.data.value  = 0
    await ClockCycles(dut.clk, 1)
    # print_chip_state(dut)

def channel_index(channel):
    if channel == 'A' or channel == 'a':
        channel = 0
    elif channel == 'B' or channel == 'b':
        channel = 1
    elif channel == 'C' or channel == 'c':
        channel = 2
    assert 0 <= channel and channel <= 2
    return channel

def inverted_channel_mask(channels):
    mask = 0
    if isinstance(channels, str):
        mask |= 1 if 'A' in channels or 'a' in channels else 0
        mask |= 2 if 'B' in channels or 'b' in channels else 0
        mask |= 4 if 'C' in channels or 'c' in channels else 0
    else:
        mask = channels
    assert 0 <= mask and mask <= 7
    return ~mask & 7

async def set_tone(dut, channel, frequency=-1, period=-1):
    channel = channel_index(channel)
    if frequency > 0:
        period = MASTER_CLOCK // (16 * frequency)
    assert 0 <= period  and period <= 4095
    await set_register(dut, channel*2+0, period & 0xFF)         # Tone A/B/C: set fine tune period
    if period > 0xFF:
        await set_register(dut, channel*2+1, period >> 8)       # Tone A/B/C: set coarse tune period

async def set_noise(dut, frequency=-1, period=-1):
    if frequency > 0:
        period = MASTER_CLOCK // (16 * frequency)
    assert 0 <= period and period <= 31
    await set_register(dut, 6, period & 31)                     # Noise: set period

async def set_mixer(dut, noises_on=0b000, tones_on=0b000):
    print((inverted_channel_mask(noises_on) << 3), inverted_channel_mask(tones_on))
    await set_register(dut, 7, (inverted_channel_mask(noises_on) << 3) | inverted_channel_mask(tones_on))

async def set_mixer_off(dut):
    await set_mixer(dut, noises_on=0, tones_on=0)

async def set_volume(dut, channel, vol=0, envelope=False):
    channel = channel_index(channel)
    if vol < 0:
        envelope = True
        vol = 0
    assert 0 <= channel and channel <= 2
    assert 0 <= vol     and vol <= 15
    await set_register(dut, 8+channel, (16 if envelope else 0) | vol)

@cocotb.test()
async def test_dac_control(dut):
    await reset(dut)

    dut._log.info("disable tones and noises on all channels")
    await set_mixer_off(dut)                                    # Mixer: disable all tones and noises, channels are controller by volume alone
    await set_volume(dut, 'A', 0)                               # Channel A: no envelope, set channel A to "fixed" level controlled by volume
    await set_volume(dut, 'B', 0)                               # Channel B: -- // --
    await set_volume(dut, 'C', 0)                               # Channel C: -- // --

    for chan in 'ABC':
        for vol in range(16):
            await set_volume(dut, chan, vol)                    # Channel A/B/C: set volume
            expected = (1 << (vol-1)) if vol > 0 else 0
            await ClockCycles(dut.clk, 4)
            # for i in range(10):
            #     await ClockCycles(dut.clk, 1)
            #     print(dut.channel_A_dac_ctrl.value, dut.channel_B_dac_ctrl.value, dut.channel_C_dac_ctrl.value)
            if chan == 'A':
                assert dut.channel_A_dac_ctrl == expected
            elif chan == 'B':
                assert dut.channel_B_dac_ctrl == expected
            elif chan == 'C':
                assert dut.channel_C_dac_ctrl == expected
        await set_volume(dut, chan, 0)                          # Channel A/B/C: silence

    await set_mixer(dut, tones_on='ABC')                        # Mixer: enable all tones
    for chan in 'ABC':
        await set_tone(dut, chan, period=1)                     # All channels: set tone to highest frequency 
    for vol in range(16):
        for chan in 'ABC':
            await set_volume(dut, chan, vol)                    # All channels: set volume
        await ClockCycles(dut.clk, 4)
        expected = (1 << (vol-1)) if vol > 0 else 0
        assert dut.channel_A_dac_ctrl == expected
        assert dut.channel_B_dac_ctrl == expected
        assert dut.channel_C_dac_ctrl == expected
        await ClockCycles(dut.clk, 8)
        assert dut.channel_A_dac_ctrl == 0
        assert dut.channel_B_dac_ctrl == 0
        assert dut.channel_C_dac_ctrl == 0
        await ClockCycles(dut.clk, 8)

    await set_mixer(dut, tones_on='AC')                         # Mixer: enable A and C tones
    for vol in range(16):
        for chan in 'ABC':
            await set_volume(dut, chan, vol)                    # All channels: set volume
        await ClockCycles(dut.clk, 4)
        expected = (1 << (vol-1)) if vol > 0 else 0
        assert dut.channel_A_dac_ctrl == expected
        assert dut.channel_B_dac_ctrl == expected
        assert dut.channel_C_dac_ctrl == expected
        await ClockCycles(dut.clk, 8)
        assert dut.channel_A_dac_ctrl == 0
        assert dut.channel_B_dac_ctrl == expected               # Channel B is not driven by the tone generator!
        assert dut.channel_C_dac_ctrl == 0
        await ClockCycles(dut.clk, 8)

    await done(dut)
