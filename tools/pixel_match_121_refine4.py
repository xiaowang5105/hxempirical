from pathlib import Path
p=Path('src/main/java/com/hexie/stata/HxWorkbench.java')
s=p.read_text(encoding='utf-8')

badge=r'''
      private JComponent exactNumberBadge(String number, Color color) {
         JComponent badge=new JComponent(){
            @Override protected void paintComponent(Graphics g0){
               Graphics2D g=(Graphics2D)g0.create(); g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON); int d=Math.min(getWidth(),getHeight())-2; int x=(getWidth()-d)/2; int y=(getHeight()-d)/2; g.setColor(color); g.fillOval(x,y,d,d); g.setColor(Color.WHITE); g.setFont(getFont().deriveFont(Font.BOLD,11.0F)); java.awt.FontMetrics fm=g.getFontMetrics(); int tx=(getWidth()-fm.stringWidth(number))/2; int ty=(getHeight()-fm.getHeight())/2+fm.getAscent(); g.drawString(number,tx,ty); g.dispose();
            }
         }; badge.setPreferredSize(new Dimension(31,31)); badge.setMinimumSize(new Dimension(31,31)); badge.setMaximumSize(new Dimension(31,31)); return badge;
      }
'''
if 'private JComponent exactNumberBadge' not in s:
    marker='      private JPanel exactLinearStep('
    pos=s.find(marker)
    if pos<0: raise SystemExit('linear step marker missing')
    s=s[:pos]+badge+'\n'+s[pos:]

# Replace linear recommendation step badge with a fixed circular painter.
old='JLabel n=new JLabel(number,SwingConstants.CENTER); n.setOpaque(true); n.setBackground(color); n.setForeground(Color.WHITE); n.setFont(n.getFont().deriveFont(Font.BOLD,12.0F)); n.setPreferredSize(new Dimension(30,30));'
s=s.replace(old,'JComponent n=this.exactNumberBadge(number,color);')

# Replace OneClick recommendation badges.
old2='JLabel n=new JLabel(rs[i][0],SwingConstants.CENTER); n.setOpaque(true); n.setBackground(rc[i]); n.setForeground(Color.WHITE); n.setPreferredSize(new Dimension(29,29));'
s=s.replace(old2,'JComponent n=this.exactNumberBadge(rs[i][0],rc[i]);')
# Replace OneClick quick-step badges.
old3='JLabel n=new JLabel(q[i][0],SwingConstants.CENTER); n.setOpaque(true); n.setBackground(new Color(34,109,246)); n.setForeground(Color.WHITE); n.setFont(n.getFont().deriveFont(Font.BOLD,12.0F)); n.setPreferredSize(new Dimension(31,31));'
s=s.replace(old3,'JComponent n=this.exactNumberBadge(q[i][0],new Color(34,109,246));')

# Make compact method buttons fit their full labels.
needle='JToggleButton b=new JToggleButton(mv[i]); styleSecondaryButton(b);'
s=s.replace(needle,'JToggleButton b=new JToggleButton(mv[i]); b.setFont(b.getFont().deriveFont(8.5F)); b.setMargin(new Insets(0,2,0,2)); styleSecondaryButton(b);')

p.write_text(s,encoding='utf-8')
print('HX_PIXEL_MATCH_121_REFINE4_OK')
