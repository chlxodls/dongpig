import streamlit as st
st.title('프로미스나인')
a=st.text_input('이름을 입력하세요!')
b=st.selectbox('좋아하는 맴버를 입력하세요',['송하영','백지헌','이나경'])
if st.button('인사말 생성'):
  st.write('반갑습니다')
  st.info(a+'님, 안녕하세요!')
  st.warning(b+'를 좋아하시는군요!')
  st.error('좋은 선택입니다!')
  st.balloons()
