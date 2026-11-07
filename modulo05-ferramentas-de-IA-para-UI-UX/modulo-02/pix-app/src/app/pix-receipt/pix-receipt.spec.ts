import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PixReceiptComponent } from './pix-receipt';

describe('PixReceipt', () => {
  let component: PixReceiptComponent;
  let fixture: ComponentFixture<PixReceiptComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PixReceiptComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PixReceiptComponent);
    fixture.componentRef.setInput('nome', 'Ana');
    fixture.componentRef.setInput('valor', 10);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
