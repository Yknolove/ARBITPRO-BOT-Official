import importlib
import pytest


def test_filters_import():
    module = importlib.import_module('aiogram.filters')
    assert hasattr(module, 'CommandStart')
    assert hasattr(module, 'Command')


@pytest.mark.asyncio
async def test_fsm_context():
    from aiogram.fsm.context import FSMContext

    ctx = FSMContext()
    await ctx.set_state('state1')
    await ctx.update_data(foo='bar')
    data = await ctx.get_data()
    assert data == {'foo': 'bar'}
    await ctx.clear()
    assert await ctx.get_data() == {}


def test_fsm_state_import():
    module = importlib.import_module('aiogram.fsm.state')
    assert hasattr(module, 'State')
    assert hasattr(module, 'StatesGroup')


def test_f_filters():
    from aiogram import F

    assert hasattr(F, 'text')
    assert hasattr(F, 'data')
    assert hasattr(F.text, 'startswith')
    assert hasattr(F.text, 'regexp')
